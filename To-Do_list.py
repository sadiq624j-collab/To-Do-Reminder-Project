'''CREATING SIMPLE TO-DO LIST MICRO PROJECT USING ONLY PYTHON'''

Leader = "Sadiq Raza"
Member_1 = "Masoom Khan"
Member_3 = "Alfiya Shaikh"
Member_4 = "Amaan Kungle"

tasks = []

def show_menu():
    print("\n--- To-Do List ---")
    print("1. Add Task")
    print("2. View Task")
    print("3. Mark Task as Done")
    print("4. Delete Task")
    print("5. Exit")

def add_task():
    task = input("Enter task: ")
    tasks.append({"task":task, "Done":False})
    print(f"Task '{task}'  added!")

def view_task():
    if not tasks:
        print("No tasks yet!")
        return
    print("\nyour Tasks:")
    for index, task in enumerate(tasks,start=1):
        status = "✅" if task["Done"] else "❌"   
        print(f"{index}. {task['task']} [{status}]")

def mark_done():
    view_task()
    if not tasks:
        print("There is no task available in your list")
        return
    try:
        index = int(input("Enter task number to mark done: "))-1
        if 0 <= index < len(tasks):  
            tasks[index]['Done'] = True
            print("Marked as Done!")
        else:
            print("Please enter a valid number: ")
    except ValueError:
        print("Please enter a valid number: ")

def delete_task():
    view_task()
    if not tasks:
        print("There is no task available in your list")
        return 
    try:
        index = int(input("Enter task number to mark done: "))-1
        if 0 <= index < len(tasks):
            removed = tasks.pop(index)
            print(f"Deleted task: {removed['task']}")
        else:
            print("Invalid Number!")
    except ValueError:
        print("Please enter a valid number!")

while True:
    show_menu()
    choice = input("Choose an option (1-5): ")

    if choice == '1':
        add_task()
    elif choice == '2':
        view_task()
    elif choice == '3':
        mark_done()
    elif choice == '4':
        delete_task()
    elif choice == '5':
        print("Good Bye!!") 
        break
    else: 
        print("Invalid choice. Try Again")
        print("Choose number between (1-5) only")


              
        







