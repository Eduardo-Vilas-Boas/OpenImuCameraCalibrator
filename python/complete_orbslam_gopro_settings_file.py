from scipy.spatial.transform import Rotation as R
import json, numpy as np
from argparse import ArgumentParser


if __name__ == "__main__":

    parser = ArgumentParser(
        "OpenCameraCalibrator - Average noise and random walk values from sensor log files"
    )
    # Cast the input to string, int or float type
    parser.add_argument(
        "--cam_calib_file_path",
        default="Calibration_Datasets/Calibration/cam/cam_calib_GX010248_fi_1.0.json",
        help="Path to camera calibration file",
    )

    parser.add_argument(
        "--cam_imu_calib_file_path",
        default="Calibration_Datasets/Calibration/cam_imu/cam_imu_calib_result_GX010249.json",
        help="Path to camera imu calibration file",
    )

    args = parser.parse_args()

    with open(args.cam_calib_file_path, "r") as f:
        data = json.load(f)

        assert (
            data["image_height"] == 2028
        ), "Image height should be 2028 - image downsample factor 1"
        assert (
            data["image_width"] == 2704
        ), "Image width should be 2704 - image downsample factor 1"

        print(f"Camera1.fx: {data['intrinsics']['focal_length']}")
        print(
            f"Camera1.fy: {data['intrinsics']['focal_length'] * data['intrinsics']['aspect_ratio']}"
        )
        print(f"Camera1.cx: {data['intrinsics']['principal_pt_x']}")
        print(f"Camera1.cy: {data['intrinsics']['principal_pt_y']}")
        print("")

        print(f"Camera1.k1: {data['intrinsics']['radial_distortion_1']}")
        print(f"Camera1.k2: {data['intrinsics']['radial_distortion_2']}")
        print(f"Camera1.k3: {data['intrinsics']['radial_distortion_3']}")
        print(f"Camera1.k4: {data['intrinsics']['radial_distortion_4']}")
        print("")

        print("# Camera resolution")
        print(f"Camera.width: {data['image_width']}")
        print(f"Camera.height: {data['image_height']}")
        print("")

        assert abs(data["fps"] - 60) < 0.15, "Camera fps should be close to 60"
        print("# Camera frames per second")
        print("Camera.fps: 60")
        print("")

    print(
        "# Color order of the images (0: BGR, 1: RGB. It is ignored if images are grayscale)"
    )
    print("Camera.RGB: 1")
    print("")

    print("# Transformation from camera to imu (body frame)")
    print("# calibrated with OpenICC https://github.com/urbste/OpenImuCameraCalibrator")
    print("IMU.T_b_c1: !!opencv-matrix")
    print("    rows: 4")
    print("    cols: 4")
    print("    dt: f")
    print("# permuted calibration")
    print("# perm_mat = np.array([")
    print("# [0,0,1,0],")
    print("# [1,0,0,0],")
    print("# [0,1,0,0],")
    print("# [0,0,0,1]")
    print("# ])")
    print("# mat = perm_mat @ open_cam_imu_tbc")
    with open(args.cam_imu_calib_file_path, "r") as f:
        data = json.load(f)
        q_cam_to_imu = [
            data["q_i_c"]["x"],
            data["q_i_c"]["y"],
            data["q_i_c"]["z"],
            data["q_i_c"]["w"],
        ]
        t_cam_to_imu = [data["t_i_c"]["x"], data["t_i_c"]["y"], data["t_i_c"]["z"]]

        T_cam_to_imu = np.eye(4)
        T_cam_to_imu[:3, :3] = R.from_quat(q_cam_to_imu).as_matrix()
        T_cam_to_imu[:3, 3] = t_cam_to_imu

        indent = " " * 4
        for i in range(4):
            row = list(T_cam_to_imu[i, :])

            if i == 0:
                formatted_row = " ".join(
                    (f"{x.item()},").ljust(30) for x in row
                )  # x.item() gets Python float

            elif i < 3:
                formatted_row = " ".join(
                    (f"{x.item()},").ljust(30) for x in row
                )  # x.item() gets Python float
            else:
                formatted_row = " ".join(
                    (f"{x.item()},").ljust(30) for x in row[:-1]
                ) + f" {row[-1]}".ljust(31)

            if i == 0:
                print(f"{indent}data: [{formatted_row}")
            elif i == 3:
                print(f"{indent}       {formatted_row}]")
            else:
                print(f"{indent}       {formatted_row}")
