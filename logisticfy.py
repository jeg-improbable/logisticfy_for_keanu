
import argparse
import json
import pprint
import csv
import logging
import random

parser = argparse.ArgumentParser()
#parser.add_argument('-n','--number',help='number of fields',type=int,required=True)
parser.add_argument('-p','--predict',help='field to predict', type=str)
parser.add_argument('-d','--data',required=False)
parser.add_argument('-o','--output')
parser.add_argument('-s','--subsample',type=float)

def determine_data(args):

    independent_variables = {}
    dependent_variable = {}
    with open(args.data, 'r') as csvfile:
        data = csv.DictReader(csvfile)
        print(data.fieldnames)

        prediction_index = len(data.fieldnames)-1
        print("data: {}".format(data))
        print(type(data.fieldnames))
        if(args.predict):
            prediction_index = data.fieldnames.index(args.predict)
        else:
            logging.info("No --predict field indicated so assuming we want to predict the last column")


        for i,n in enumerate(data.fieldnames):
            if i == prediction_index:
                dependent_variable[n] = []
                dependent_name = n
            else:
                independent_variables[n] = []

        for r in data:
            if random.random() > args.subsample:

                continue

            for k in independent_variables:
                independent_variables[k].append(float(r[k]))
            dependent_variable[dependent_name].append(float(r[dependent_name]))

    #pprint.pprint(dependent_variable)
    #pprint.pprint(independent_variables)

    return [dependent_variable,independent_variables]


def main(args):

    [dependent, independent] = determine_data(args)

    vertices = []
    mults = []

    for i in range(0, len(independent.keys())+1):

        b = {
            'name': "b{}".format(i),
            'type': "gaussian",
            'mean': 0.0,
            'std': 5.0,
            'report_final_value': True
        }

        vertices.append(b)

        if(i>0):

            independent_name = list(independent.keys())[i-1]

            x = {
                'name': '{}'.format(independent_name),
                'type': 'double_constant',
                'value': 1.0
            }
            vertices.append(x)

            m = {
                'name': 'b{}{}'.format(i, independent_name),
                'type': 'multiplication',
                'a': 'b{}'.format(i),
                'b': '{}'.format(independent_name)
            }
            vertices.append(m)
            mults.append(m)

        else:
            mults.append(b)

    #make b_i * x_i nodes

    a = mults.pop()

    last_name = a['name']

    while(mults):
        b = mults.pop()
        this_name = '{}+{}'.format(last_name,b['name'])
        a = {
                'name': this_name,
                'type': 'addition',
                'a': last_name,
                'b': b['name']
            }
        last_name = this_name
        vertices.append(a)

    print(last_name)

    vertices+= [
        {
            "name": "e^({})".format(last_name),
            "type": "power",
            "base": 2.718281828459,
            "exponent": "{}".format(last_name)
        },
        {
            "name": "1+e^({})".format(last_name),
            "type": "addition",
            "a": 1.0,
            "b": "e^({})".format(last_name)
        },
        {
            "name": "e^({})/(1+e^({})".format(last_name,last_name),
            "type": "division",
            "numerator": "e^({})".format(last_name),
            "denominator": "1+e^({})".format(last_name)
        },

        {
            "name": "{}".format(list(dependent.keys())[0]),
            "type": "gaussian",
            "mean": "e^({})/(1+e^({})".format(last_name,last_name),
            "std": 1.0
        }
    ]

    output_object = dict(network=vertices,observations=[])

    for k in independent:
        output_object['observations'].append({'name':k,'samples':independent[k],'type':'input'})

    output_object['observations'].append({'name':list(dependent.keys())[0],'samples':dependent[list(dependent.keys())[0]],'type':'output'})


    with open(args.output,'w') as f:
        json.dump(output_object,f,sort_keys=True,indent=4, separators=(',', ': '))


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)