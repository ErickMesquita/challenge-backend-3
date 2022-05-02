import datetime
import os
import pandas as pd
from numpy import datetime64

from application.tests.pytest_fixtures import resources_path
from application.controller.transactions_utils import clean_uploaded_transactions



t_utils.save_uploaded_file(file, upload_folder_path, current_user.id)