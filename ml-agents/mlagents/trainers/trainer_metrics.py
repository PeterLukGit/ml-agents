# # Unity ML-Agents Toolkit
import logging
import csv
from time import time

LOGGER = logging.getLogger("mlagents.trainers")

class TrainerMetrics(object):
    """
        Helper class to track, write training metrics. Tracks time since object
        of this class is initialized.
    """

    def __init__(self, path: str, brain_name: str):
        """
        :str path: Fully qualified path where CSV is stored.
        :str brain_name: Identifier for the Brain which we are training
        """
        self.path = path
        self.brain_name = brain_name
        self.FIELD_NAMES = ['Brain name', 'Time to update policy',
                            'Time since start of training', 'Time for last experience collection',
                            'Number of experiences used for training', 'Mean return']
        self.rows = []
        self.time_start_experience_collection = None
        self.time_training_start = time()
        self.last_buffer_length = None
        self.last_mean_return = None
        self.time_policy_update_start = None
        self.delta_last_experience_collection = None
        self.delta_policy_update = None

    def start_experience_collection_timer(self):
        """
        Inform Metrics class that experience collection is starting. Intended to be idempotent
        """
        if self.time_start_experience_collection is None:
            self.time_start_experience_collection = time()

    def end_experience_collection_timer(self):
        """
        Inform Metrics class that experience collection is done.
        """
        self.delta_last_experience_collection = time() - self.time_start_experience_collection
        self.time_start_experience_collection = None

    def start_policy_update_timer(self, number_experiences: int, mean_return: float):
        """
        Inform Metrics class that policy update has started.
        :int number_experiences: Number of experiences in Buffer at this point.
        :float mean_return: Return averaged across all cumulative returns since last policy update
        """
        self.last_buffer_length = number_experiences
        self.last_mean_return = mean_return
        self.time_policy_update_start = time()

    def end_policy_update(self):
        """
        Inform Metrics class that policy update has started.
        """
        self.delta_policy_update = time() - self.time_policy_update_start
        delta_train_start = time() - self.time_training_start
        LOGGER.debug(" Policy Update Training Metrics for {}: "
                     "\n\t\tTime to update Policy: {:0.3f} s \n"
                     "\t\tTime elapsed since training: {:0.3f} s \n"
                     "\t\tTime for experience collection: {:0.3f} s \n"
                     "\t\tBuffer Length: {} \n"
                     "\t\tReturns : {:0.3f}\n"
                     .format(self.brain_name, self.delta_policy_update,
                             delta_train_start, self.delta_last_experience_collection,
                             self.last_buffer_length, self.last_mean_return))
        row = [self.brain_name]
        row.extend(format(c, '.3f') if isinstance(c) is float else c
                   for c in [self.delta_policy_update, delta_train_start,
                             self.delta_last_experience_collection,
                             self.last_buffer_length, self.last_mean_return])
        self.rows.append(row)

    def write_training_metrics(self):
        """
        Write Training Metrics to CSV
        """
        with open(self.path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(self.FIELD_NAMES)
            for row in self.rows:
                writer.writerow(row)
