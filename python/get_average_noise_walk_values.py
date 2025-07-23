import re
import os
from argparse import ArgumentParser


def extract_values_from_lines(text, sensor_type):
    data = {}
    lines = text.splitlines()
    axes = ["x", "y", "z"]
    current_axis = None
    collecting = False
    white_noise_count = 0

    for line in lines:
        line = line.strip()

        # Detect start of section
        for axis in axes:
            if line.lower().startswith(f"{sensor_type.lower()} {axis}"):
                current_axis = f"{sensor_type.lower()}_{axis}"
                data[current_axis] = {"bias_instability": None, "white_noise": None}
                collecting = True
                white_noise_count = 0
                break

        if not collecting or current_axis is None:
            continue

        # Handle Bias Instability
        if "bias instability" in line.lower():
            parts = line.split()
            try:
                value = float(parts[2])
            except (IndexError, ValueError):
                continue

            if "at" in line.lower():
                # Time-specific value (for gyro)
                data[current_axis]["bias_instability"] = value
            elif sensor_type.lower() == "acc":
                # Only one line in acc blocks
                data[current_axis]["bias_instability"] = value

        # Handle White Noise
        elif "white noise" in line.lower():
            parts = line.split()
            try:
                value = float(parts[2])
            except (IndexError, ValueError):
                continue

            white_noise_count += 1

            if sensor_type.lower() == "gyro" and white_noise_count == 2:
                data[current_axis]["white_noise"] = value
            elif sensor_type.lower() == "acc" and white_noise_count == 1:
                data[current_axis]["white_noise"] = value

        # Detect end of block
        elif "-------------------" in line:
            current_axis = None
            collecting = False

    # Remove incomplete axes
    data = {
        k: v
        for k, v in data.items()
        if v["bias_instability"] is not None and v["white_noise"] is not None
    }

    return data


def extract_average_frequency(text):
    """
    Extracts frequency values for gyro and accelerometer axes (x, y, z) and returns the average.
    """
    freq_pattern = re.compile(r"(gyr|acc)_[xyz]\s+freq\s+([0-9.]+)", re.IGNORECASE)
    frequencies = []

    for match in freq_pattern.finditer(text):
        freq_value = float(match.group(2))
        frequencies.append(freq_value)

    if not frequencies:
        return None  # or raise an error if preferred

    avg_freq = sum(frequencies) / len(frequencies)
    return avg_freq


def main():

    parser = ArgumentParser(
        "OpenCameraCalibrator - Average noise and random walk values from sensor log files"
    )
    # Cast the input to string, int or float type
    parser.add_argument(
        "--path",
        default="Calibration_Datasets/IMU_Noise/",
        help="Path to sensor data folder",
    )

    args = parser.parse_args()

    acc_noise = 0
    acc_walk = 0
    gyro_noise = 0
    gyro_walk = 0
    freq = 0

    files_number = 0

    for file in os.listdir(args.path):
        if file.endswith("results.txt"):
            with open(os.path.join(args.path, file), "r") as f:
                log_data = f.read()

                gyro_data = extract_values_from_lines(log_data, "Gyro")
                acc_data = extract_values_from_lines(log_data, "acc")

                print(f"Gyroscope Noise and Random Walk for file {file}:")
                gyro_noise_file = 0
                gyro_walk_file = 0

                for axis, vals in gyro_data.items():
                    print(
                        f"{axis}: Bias Instability = {vals['bias_instability']} rad/s, White Noise = {vals['white_noise']} rad/s^2"
                    )
                    gyro_noise_file += vals["white_noise"]
                    gyro_walk_file += vals["bias_instability"]

                gyro_noise_file /= len(gyro_data)
                gyro_walk_file /= len(gyro_data)

                print("\nAccelerometer Noise and Random Walk:")
                acc_noise_file = 0
                acc_walk_file = 0

                for axis, vals in acc_data.items():
                    print(
                        f"{axis}: Bias Instability = {vals['bias_instability']} m/s^2, White Noise = {vals['white_noise']} m/s^2"
                    )
                    acc_noise_file += vals["white_noise"]
                    acc_walk_file += vals["bias_instability"]

                acc_noise_file /= len(acc_data)
                acc_walk_file /= len(acc_data)
                print("\n" + "=" * 50 + "\n")

                files_number += 1

                acc_noise += acc_noise_file
                acc_walk += acc_walk_file
                gyro_noise += gyro_noise_file
                gyro_walk += gyro_walk_file

                freq += extract_average_frequency(log_data)

    if files_number > 0:
        print(f"IMU.NoiseGyro: {gyro_noise / files_number} # rad/s^0.5")
        print(f"IMU.NoiseAcc: {acc_noise / files_number} # m/s^1.5")
        print(f"IMU.GyroWalk: {gyro_walk / files_number} # rad/s^1.5")
        print(f"IMU.AccWalk: {acc_walk / files_number} # m/s^2.5")
        print(f"IMU.Frequency: { freq / files_number} # Hz")


if __name__ == "__main__":
    main()
