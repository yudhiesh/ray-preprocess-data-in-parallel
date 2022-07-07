import psutil
import ray

from src.process_files.preprocess import main_file_processor
from src.process_files.preprocess_ray import main_file_processor_ray


if __name__ == "__main__":
    ray.init(num_cpus=psutil.cpu_count())
    main_file_processor_ray()
