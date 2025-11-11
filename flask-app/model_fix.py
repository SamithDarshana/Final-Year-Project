import tensorflow as tf
from keras import regularizers, models

# === load the original model fully ===
old_model = tf.keras.models.load_model("models/model.h5", compile=False)

# === re-create a new Sequential/Functional model ===
input_layer = old_model.input
# take output before last layer if you need
x = old_model.layers[-2].output
output_layer = old_model.layers[-1].output
new_model = models.Model(inputs=input_layer, outputs=output_layer)

# === reapply correct regularizers ===
for layer in new_model.layers:
    if hasattr(layer, "kernel_regularizer") and layer.kernel_regularizer is not None:
        layer.kernel_regularizer = regularizers.l2(0.01)

# === save in new format ===
new_model.save("models/model_fixed.keras")
print("✅ Clean model rebuilt and saved as models/model_fixed.keras")
