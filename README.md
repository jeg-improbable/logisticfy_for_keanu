## Usage
Point logisticfy at a CSV file, let it know which field should be predicted, and then let it know where to write. If
no `--prediction` field is provided, the script assumes that last column should be predicted.

`python logisticfy --data data_classification.csv --predict y --output output.json`

The produced `json` file works with the network serialization code [here](https://github.com/jeg-improbable/keanu/tree/serialized-regression/keanu-examples/serializationExample/src)
