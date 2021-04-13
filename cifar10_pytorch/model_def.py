"""
CNN on Cifar10 from Keras example:
https://github.com/fchollet/keras/blob/master/examples/cifar10_cnn.py
"""

import tempfile
from typing import Any, Dict, Sequence, Tuple, Union, cast
import time
import torch
import torchvision
from torch import nn
from torchvision import transforms

from determined.pytorch import DataLoader, PyTorchTrial, PyTorchTrialContext

# Constants about the data set.
IMAGE_SIZE = 32
NUM_CHANNELS = 3
NUM_CLASSES = 10

TorchData = Union[Dict[str, torch.Tensor], Sequence[torch.Tensor], torch.Tensor]


def accuracy_rate(predictions: torch.Tensor, labels: torch.Tensor) -> float:
    """Return the accuracy rate based on dense predictions and sparse labels."""
    assert len(predictions) == len(labels), "Predictions and labels must have the same length."
    assert len(labels.shape) == 1, "Labels must be a column vector."

    return (  # type: ignore
        float((predictions.argmax(1) == labels.to(torch.long)).sum()) / predictions.shape[0]
    )


class Flatten(nn.Module):
    def forward(self, *args: TorchData, **kwargs: Any) -> torch.Tensor:
        assert len(args) == 1
        x = args[0]
        assert isinstance(x, torch.Tensor)
        return x.contiguous().view(x.size(0), -1)


class CIFARTrial(PyTorchTrial):
    def __init__(self, context: PyTorchTrialContext) -> None:
        self.context = context

        # Create a unique download directory for each rank so they don't overwrite each
        # other when doing distributed training.


        # Cache the dataset after the first time
        self.download_directory = f"/mnt/data/cifar10/rank{self.context.distributed.get_rank()}"
        # self.download_directory = tempfile.mkdtemp()

        self.model = self.context.wrap_model(nn.Sequential(
            nn.Conv2d(NUM_CHANNELS, IMAGE_SIZE, kernel_size=(3, 3)),
            nn.ReLU(),
            nn.Conv2d(32, 32, kernel_size=(3, 3)),
            nn.ReLU(),
            nn.MaxPool2d((2, 2)),
            nn.Dropout2d(self.context.get_hparam("layer1_dropout")),
            nn.Conv2d(32, 64, (3, 3), padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, (3, 3)),
            nn.ReLU(),
            nn.MaxPool2d((2, 2)),
            nn.Dropout2d(self.context.get_hparam("layer2_dropout")),
            Flatten(),
            nn.Linear(2304, 512),
            nn.ReLU(),
            nn.Dropout2d(self.context.get_hparam("layer3_dropout")),
            nn.Linear(512, NUM_CLASSES),
        ))

        self.optimizer = self.context.wrap_optimizer(torch.optim.RMSprop(  # type: ignore
            self.model.parameters(),
            lr=self.context.get_hparam("learning_rate"),
            weight_decay=self.context.get_hparam("learning_rate_decay"),
            alpha=0.9,
        ))
        self.timer = time.time()

    def train_batch(
        self, batch: TorchData, epoch_idx: int, batch_idx: int
    ) -> Dict[str, torch.Tensor]:

        now = time.time()
        dur = now - self.timer
        self.timer = now


        batch = cast(Tuple[torch.Tensor, torch.Tensor], batch)
        data, labels = batch

        output = self.model(data)
        loss = torch.nn.functional.cross_entropy(output, labels)
        accuracy = accuracy_rate(output, labels)

        self.context.backward(loss)
        self.context.step_optimizer(self.optimizer)

        metrics = {"loss": loss, "train_error": 1.0 - accuracy, "train_accuracy": accuracy}

        if dur < 10:
            throughput = self.context.get_global_batch_size() / dur
            metrics["batch_duration"] = dur
            metrics["throughput"] = throughput
        else:
            metrics["batch_duration"] = 0
            metrics["throughput"] = 0

        return metrics


    def evaluate_batch(self, batch: TorchData) -> Dict[str, Any]:
        """
        Calculate validation metrics for a batch and return them as a dictionary.
        This method is not necessary if the user defines evaluate_full_dataset().
        """
        batch = cast(Tuple[torch.Tensor, torch.Tensor], batch)
        data, labels = batch

        output = self.model(data)
        accuracy = accuracy_rate(output, labels)
        return {"validation_accuracy": accuracy, "validation_error": 1.0 - accuracy}

    def build_training_data_loader(self) -> Any:
        transform = transforms.Compose(
            [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
        )
        trainset = torchvision.datasets.CIFAR10(
            root=self.download_directory, train=True, download=True, transform=transform
        )
        return DataLoader(trainset, batch_size=self.context.get_per_slot_batch_size())

    def build_validation_data_loader(self) -> Any:
        transform = transforms.Compose(
            [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
        )
        valset = torchvision.datasets.CIFAR10(
            root=self.download_directory, train=False, download=True, transform=transform
        )

        return DataLoader(valset, batch_size=self.context.get_per_slot_batch_size())
