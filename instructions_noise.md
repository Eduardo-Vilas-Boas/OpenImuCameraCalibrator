# Instructions

*Note:* All datasets should be placed inside a bigger `Calibration_Datasets` folder, in the project directory.


# Estimate GoPro intrinsics

For this example I am using a video recorded with the GoPro9. Please read this paper[1] on how to record the video and details on how the method works. Remember to let the camera stand still for > 40 seconds in the beginning. The IMU bias will be estimated in this phase. This is also a parameter you need to supply to the calibration script.

Place the video in `Calibration_Datasets/IMU_Intrinsics`.

1. Start by extracting the telemetry of the calibration video:
    ```python python/run_pygpmf_extraction.py --path=<calibration_video_directory>```
2. Use the generated telemetry files to run the static imu calibration. If successfull this script will output a `json file static_calib_result.json containing IMU intrinsics for your camera`.
    ```python python/static_multipose_imu_calibration.py --path_static_calib_dataset=<calibration_dataset> --initial_static_duration_s=40 --path_to_build=<path_to_build>/applications```


# Camera calibration

1. Mount the FishEye camera lense.
2. Set the camera settings by following the UMI (Dataset Collection Instructions)[https://swanky-sphere-ad1.notion.site/UMI-Data-Collection-Instruction-4db1a1f0f2aa4a2e84d9742720428b4c].
3. Print the (calibration board)[https://github.com/urbste/OpenImuCameraCalibrator/blob/master/resource/board.pnghttps://github.com/urbste/OpenImuCameraCalibrator/blob/master/resource/board.png].
4. Collect a calibration dataset following the instructions defined in [OpenImuCameraCalibrator](https://github.com/urbste/OpenImuCameraCalibrator/blob/master/docs/gopro_calibration.md). Place the dataset in `Calibration_Datasets/Calibration`.
5. Run the calibration (use the json file static_calib_result.json created during the `Estimate GoPro intrinsics` step). `This process can take several hours`.
    - ```python python/run_gopro_calibration.py --path_to_build=<path_to_build>/applications --path_calib_dataset=<calibration_dataset> --checker_size_m=<square_size> --image_downsample_factor=1 --camera_model=FISHEYE --path_to_imu_intrinsics=<path_to_static_calib_result.json>```
6. Copy the `cam/cam_calib_<video_name>_fi_1.0.json` file content and replace the original content for `example/calibration/gopro_intrinsics_2_7k.json`. 


# Create GoPro ORBSLAM 3 settings

## Estimate sensors bias and noise

1. Record a > 2h video keeping your camera completely still. Use the lowest resolution and FPS setting, as we do not need the video feed for this. In addition, you can cover the lens. A video of a black screen will remain quite small. Place the videos in `Calibration_Datasets/IMU_Noise`.
2. Still this will create multiple video files, so we need to extract the telemetry from each.
    - ```python python/run_pygpmf_extraction.py --path=<video_folder_path>```
3. For each  file (there should be 2 or 3 files, ending in .json, not in _pygpmf.json), execute the following script. The output file should have the same parent directory and name, but end in `_results.txt`.
    - ```./build/applications/fit_allan_variance --telemetry_json=<telemetry_json_file>.json > <telemetry_json_file>_results.txt```
4. For getting the average values, do:
    - ```python python/get_average_noise_walk_values.py --path=<video_folder_path>```
5. Include these values on the GoPro ORBSLAM 3 settings file - `gopro12_maxlens_fisheye_settings.yaml`. Check the (original file)[https://github.com/cheng-chi/ORB_SLAM3/blob/master/Examples/Monocular-Inertial/gopro10_maxlens_fisheye_setting_v1_720.yaml] and use it as a template.

## Complete ORBSLAM 3 file

1. Execute the following instruction:
    ```python python/complete_orbslam_gopro_settings_file.py --cam_calib_file_path=Calibration_Datasets/Calibration/cam/cam_calib_<video_file_path>_fi_1.0.json --cam_imu_calib_file_path=Calibration_Datasets/Calibration/cam_imu/cam_imu_calib_result_<video_file_path>.json```
2. Include these values on the GoPro ORBSLAM 3 settings file - `gopro12_maxlens_fisheye_settings.yaml`. Check the (original file)[https://github.com/cheng-chi/ORB_SLAM3/blob/master/Examples/Monocular-Inertial/gopro10_maxlens_fisheye_setting_v1_720.yaml] and use it as a template.



# Bibliography

[1] D. Tedaldi, A. Pretto and E. Menegatti, "A Robust and Easy to Implement Method for IMU Calibration without External Equipments". In: Proceedings of the IEEE International Conference on Robotics and Automation (ICRA 2014), May 31 - June 7, 2014 Hong Kong, China, Page(s): 3042 - 3049
