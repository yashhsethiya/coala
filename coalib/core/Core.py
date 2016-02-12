from multiprocessing import Pool, Queue
from queue import Empty

from coalib.bears.BearLogMessage import BearLogMessage
from coalib.results.Result import Result


def instantiate_bears(bears)
    # TODO instantiate bears from iterable containing classes.
    pass


def dispatch_result(result):
    if isinstance(result, Result):
        pass
    elif isinstance(result, BearLogMessage)
        pass
    else:
        # Log a warning that unrecognized class was put into the com queue.
        pass


def execute(section, bears):
    # TODO Do we need section? in fact not, each bear contains a section.
    #      I need some suitable section down-propagation model... A section
    #      contains everything, from cmd-args until settings.
    # TODO Use section to get number of threads to run.
    pool = Pool()
    comq = Queue()

    async_results = [pool.map_async(bear.execute_task, bear.generate_tasks())
                     for bear in bears]

    while True:
        try:
            dispatch_result(queue.get(0.1))
        except Empty:
            # Check for finished AsyncResult's.
            for i, result in reversed(enumerate(async_results)):
                if result.ready():
                    del async_results[i]

            if not async_results:
                break
