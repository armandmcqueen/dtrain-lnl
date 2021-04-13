# Distributed Training Lunch and Learn

- We will be trying to speed up this CIFAR-10 CNN
- There is a known good configuration in `1gpu.yaml`
- The target validation accuracy is 74%


---

# PyTorch CIFAR-10 CNN Example

This example shows how to build a simple CNN on the CIFAR-10 dataset using
Determined's PyTorch API. This example is adapted from this [Keras CNN
example](https://github.com/fchollet/keras/blob/master/examples/cifar10_cnn.py).

## Files
* **model_def.py**: The core code for the model. This includes building and compiling the model.

### Configuration Files
* **1gpu.yaml**: Train the model with constant hyperparameter values.

## Data
The CIFAR-10 dataset is downloaded from https://www.cs.toronto.edu/~kriz/cifar.html.

## To Run
If you have not yet installed Determined, installation instructions can be found
under `docs/install-admin.html` or at https://docs.determined.ai/latest/index.html

Run the following command: `det -m <master host:port> experiment create -f
const.yaml .`. The other configurations can be run by specifying the appropriate
configuration file in place of `const.yaml`.

## Results
Training the model with the hyperparameter settings in `const.yaml` should yield
a validation accuracy of ~74%.
