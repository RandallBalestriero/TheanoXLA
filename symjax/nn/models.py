from . import layers, initializers


class ResidualBlockv1:
    def __init__(self, activation, dropout_rate=0.1):
        self.activation = activation
        self.dropout_rate = dropout_rate

    def __call__(self, input, width, stride, deterministic):
        nonlinear_part = layers.Conv2D(
            input, width, (3, 3), b=None, padding="SAME", strides=stride
        )
        nonlinear_part = layers.BatchNormalization(
            nonlinear_part, deterministic=deterministic, axis=[1]
        )
        nonlinear_part = self.activation(
            layers.Dropout(
                nonlinear_part,
                deterministic=deterministic,
                p=self.dropout_rate,
            )
        )
        nonlinear_part = layers.Conv2D(
            nonlinear_part, width, (3, 3), b=None, padding="SAME"
        )
        nonlinear_part = layers.BatchNormalization(
            nonlinear_part, deterministic=deterministic, axis=[1]
        )
        nonlinear_part = layers.Dropout(
            nonlinear_part, deterministic=deterministic, p=self.dropout_rate
        )

        if stride > 1 or input.shape[1] != width:
            shortcut = layers.Conv2D(input, width, (1, 1), strides=stride)
        else:
            shortcut = input
        return self.activation(shortcut + nonlinear_part)


def ResNet(input, deterministic, widths, strides, block):
    """Residual Network

    Commonly one would use `widths=[64, 64, 128, 128, 256,256, 512, 512]` and `strides=[1,1,2,1,2,1,2,1]`
    """

    initial = layers.Conv2D(input, widths[0], (3, 3), b=None, padding="SAME")
    initial = layers.BatchNormalization(initial, deterministic=deterministic, axis=[1])
    initial = block.activation(inital)
    for width, stride in zip(widths, strides):
        initial = block(
            initial, width=width, stride=stride, deterministic=deterministic
        )
    return initial


def AlexNet(input, activation):
    """AlexNet model"""
    stride_divider = int(227 / input.shape[2])

    z = activation(
        layers.Conv2D(
            input,
            96,
            (11, 11),
            strides=max(1, 4 // stride_divider),
            W=initializers.he_normal,
        )
    )
    z = layers.Pool2D(z, (3, 3), strides=(2, 2))
    z = activation(
        layers.Conv2D(z, 256, (5, 5), W=initializers.he_normal, padding="SAME")
    )
    z = layers.Pool2D(z, (3, 3), strides=(2, 2))
    z = activation(
        layers.Conv2D(z, 384, (3, 3), W=initializers.he_normal, padding="SAME")
    )
    z = activation(
        layers.Conv2D(z, 384, (3, 3), W=initializers.he_normal, padding="SAME")
    )
    z = activation(
        layers.Conv2D(z, 256, (3, 3), W=initializers.he_normal, padding="SAME")
    )
    z = layers.Pool2D(z, (3, 3), strides=(2, 2))
    z = activation(layers.Dense(z, 4096))
    z = activation(layers.Dense(z, 4096))
    return z
