import os
import logging
import json

def setup_logging(service_name, default_level=logging.INFO):
    """Setup logging configuration"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=default_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'/var/log/{service_name}/{service_name}.log')
        ]
    )
    return logging.getLogger(service_name)
