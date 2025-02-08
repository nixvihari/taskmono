#!/usr/bin/python3

from sys import argv, exit
from datetime import datetime
from json.decoder import JSONDecodeError
import json
import os

DATETIME_FORMAT_STR = "%d-%m-%Y %H:%M:%S"

#ABSOLUTE PATH for os and symlink compatibility
realpath = os.path.realpath(__file__)
dirname = os.path.dirname(realpath)
JSONPath = os.path.join(dirname,'data.json')



# HELPER FUNCTIONS

def usage():
    print('''
Options:
    //ingore the "[]" brackets, used to indicate arguments/user input

    add ["task name/desc"]
    update [taskId "new task name/desc"]
    delete [taskId]
    list
    list todo
    list done 
    list in-progress
    mark-in-progress [taskId]
    mark-done [taskId]
''')
    exit(0)


def argLengthError():
    print('too many or few arguments, use "taskmono help" to check usage')
    exit(0)


def invalidArgsError():
    print('invalid arguments, use "taskmono help" to check usage')
    exit(0)


def initTaskProperties(desc, status='todo'):
    createdAt = datetime.now().strftime(DATETIME_FORMAT_STR)
    return {'description' : desc,
            'status' : status,
            'createdAt': createdAt,
            'updatedAt': createdAt
            }


def updateTaskProperties(task,desc=None,status=None):
    taskUpdate = task.copy()
    if desc is not None:
        taskUpdate['description'] = desc
    if status is not None:
        taskUpdate['status'] = status
    taskUpdate['updatedAt'] = datetime.now().strftime(DATETIME_FORMAT_STR)
    return taskUpdate


#Function to reindex data after deleting a record, to maintain consecutive sequence of IDs
def getIndexedData(data):
    tasks = data.values()
    l = len(data)
    indices = range(1,l+1)
    indexedData = dict(zip(indices,tasks))
    return indexedData

#Read and return data.json as dict, used frequently
def getJSONData():
    with open(JSONPath,'r') as f:
        try:
            data = json.load(f)
            return data
        except JSONDecodeError:
            print('Empty task list \nStart by adding a few tasks')
            exit(0)


def printTasks(status=None):
    #using statusPool as a set for conditional filtering based on task status
    #also to reduce redundant print statements
    #status = None, as default implies user did not specify status as condition, where all status is satisfied by statusPool
    if status is None:
        statusPool = ('todo','done','in-progress')
    else:
        statusPool = set([status])
    data = getJSONData()

    print('-------------------------------------------------------------------------------------------')
    print("{:<3} {:<25} {:<15} {:<25} {:<25}".format("ID","Description", "Status", "Created At", "Updated At"))
    print('-------------------------------------------------------------------------------------------')
    for id, task in data.items():
        if task['status'] in statusPool:
            print("{:<3} {:<25} {:<15} {:<25} {:<25}".format(id,task["description"], task["status"],task["createdAt"],task["updatedAt"]))
    
    print('')




# FEATURE FUNCTIONS

def add():
    if len(argv) != 3:
        argLengthError()
    taskName = argv[2]
    newTask = initTaskProperties(desc=taskName)
    data = getJSONData()
    if os.stat(JSONPath).st_size == 0 or data == {}:
        data = {1: newTask}
        with open(JSONPath,'w') as f:
            json.dump(data, f, indent=4)
            print(f'New Task "{taskName}" \nID: 1 \nADDED')
    else:
        with open(JSONPath, 'r+') as f:
            data = json.load(f)
            lastIndex = int(list(data)[-1])
            newIndex = lastIndex + 1
            data[newIndex] = newTask
            f.truncate(0)
            f.seek(0)
            json.dump(data,f, indent=4)
            print(f'New Task "{taskName}" \nID: {newIndex} \nADDED')


def update():
    if len(argv) != 4:
        argLengthError()
    try:
        task_id = int(argv[2])
        newName = argv[3]
    except:
        invalidArgsError()

    task_id = str(task_id)
    data = getJSONData()
    if task_id not in data:
        print(f'task {task_id} does not exist')
        return None
    task = data[task_id]
    updatedTask = updateTaskProperties(task, desc=newName)
    data[task_id] = updatedTask
    
    with open(JSONPath,'w') as f:
        json.dump(data,f, indent=4)
    print(f'updated task {task_id} to {newName}')


def delete():
    if len(argv) != 3:
        argLengthError()
    try:
        task_id = int(argv[2])
    except:
        invalidArgsError()
    
    task_id = str(task_id)
    data = getJSONData()
    if task_id not in data:
        print('Task does not exist')
        return None
    
    value = data.pop(task_id)
    print(f'Task "{value["description"]}" \nID: {task_id} \nStatus: {value["status"]} \nX- DELETED -X.')
    
    ##re-index data after deletion
    indexedData = getIndexedData(data)
    with open(JSONPath,'w') as f:
        json.dump(indexedData, f, indent=4)
        print('\nDatabase Indexed')
    
    return None


def listTasks():
    if len(argv) == 2:
        print('\nAll Tasks')
        printTasks()
        return None

    elif len(argv) == 3:
        if argv[2] == 'done':
            print('\nCompleted Tasks')
            printTasks(status='done')
            return None
        
        elif argv[2] == 'todo':
            print('\nTasks to do')
            printTasks(status='todo')
            return None

        elif argv[2] == 'in-progress':
            print('\nTasks in Progress')
            printTasks(status='in-progress')
            return None

        else:
            invalidArgsError()
    else:
        argLengthError()


def markInProgress():
    if len(argv) != 3:
        argLengthError()
    try:
        taskId = int(argv[2])
    except:
        invalidArgsError()
    
    taskId = str(taskId)
    data = getJSONData()
    if taskId not in data:
        print('Task does not exist')
        return None

    task = data[taskId]
    updatedTask = updateTaskProperties(task, status='in-progress')
    data[taskId] = updatedTask

    with open(JSONPath,'w') as f:
        json.dump(data,f, indent=4)
        print(f'Task {taskId} marked in progress')

    return None


def markDone():
    if len(argv) != 3:
        argLengthError()
    try:
        taskId = int(argv[2])
    except:
        invalidArgsError()

    taskId = str(taskId)
    data = getJSONData()
    if taskId not in data:
        print('Task does not exist')
        return None

    task = data[taskId]
    updatedTask = updateTaskProperties(task, status='done')
    data[taskId] = updatedTask

    with open(JSONPath,'w') as f:
        json.dump(data, f, indent=4)
        print(f'task {taskId} marked done')

    return None


# MAIN FUNCTION

if __name__ == "__main__":
    #creates a data.json file is it doesn't exist, else opens and closes unmodified
    open(JSONPath,'a').close()
    
    args = {
        'add': add,
        'update': update,
        'delete' : delete,
        'list' : listTasks,
        'mark-in-progress': markInProgress,
        'mark-done' : markDone,
        'help' : usage
    }

    if len(argv) < 2:
        argLengthError()
    else:
        action = str(argv[1])
        if action not in args:
            invalidArgsError()
        
        #calling the feature funcntions from args dict
        args[action]()