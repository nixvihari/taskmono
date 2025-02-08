from sys import argv, exit
from datetime import datetime
import json
import os
import traceback 

DATETIME_FORMAT_STR = "%d-%m-%Y %H:%M:%S"

def usage():
    print('''
Available options:
    add
    update
    delete
    list-tasks :todo
                done 
                in-progress
    mark-in-progress
    mark-done
''')
    exit(0)

def argLengthError():
    print('too many or few arguments, use "python3 main.py help" to check usage')
    exit(0)

def invalidArgsError():
    print('invalid arguments, use "python3 main.py help" to check usage')
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


def getJSONData():
    with open('data.json','r') as f:
        return json.load(f)

def printTasks(status=None):
    if status is None:
        statusPool = ('todo','done','in-progress')
    else:
        statusPool = set(status)
    data = getJSONData()

    print('----------------------------------------------------------------------')
    print('ID Description\tStatus\tCreated At\t\tUpdated At')
    for id, task in data.items():
        if task['status'] in statusPool:
            print(f'{id}  {task["description"]}\t{task["status"]}\t{task["createdAt"]}\t{task["updatedAt"]}')


def add():
    if len(argv) != 3:
        argLengthError()
    taskName = argv[2]
    newTask = initTaskProperties(desc=taskName)
    if os.stat('data.json').st_size == 0:
        data = {1: newTask}
        with open('data.json','w') as f:
            json.dump(data, f, indent=4)
            print(f'First Task {taskName} added at index 1')
    else:
        with open('data.json', 'r+') as f:
            data = json.load(f)
            lastIndex = int(list(data)[-1])
            newIndex = lastIndex + 1
            data[newIndex] = newTask
            f.truncate(0)
            f.seek(0)
            json.dump(data,f, indent=4)
            print(f'New Task {taskName} added at index {newIndex}')

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
    
    with open('data.json','w') as f:
        json.dump(data,f, indent=4)
    print(f'updated task {task_id} to {newName}')


def delete():
    if len(argv) != 3:
        argLengthError()
    try:
        task_id = int(argv[2])
    except:
        invalidArgsError()
    
    print(f'deleted task {task_id}')

def listTasks():
    if len(argv) == 2:
        print('All Tasks')
        printTasks()
        return None

    elif len(argv) == 3:
        if argv[2] == 'done':
            print('Completed Tasks')
            printTasks(status='done')
            return None
        
        elif argv[2] == 'todo':
            print('Tasks to do')
            printTasks(status='todo')
            return None

        elif argv[2] == 'in-progress':
            print('Tasks in Progress')
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
    
    data = getJSONData()
    if taskId not in data:
        print('Task does not exist')
        return None

    task = data[taskId]
    updatedTask = updateTaskProperties(task, status='in-progress')


    print(f'Task {taskId} marked in progress')

def markDone():
    if len(argv) != 3:
        argLengthError()
    try:
        taskId = int(argv[2])
    except:
        invalidArgsError()
    print(f'task {taskId} marked done')



if __name__ == "__main__":
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
        args[action]()