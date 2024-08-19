from flask import Flask, render_template, request, redirect, url_for
import csv

app = Flask(__name__)

csvfile = 'tasks.csv'
categoriesfile = 'categories.csv'

default_categories = ['Personal', 'School', 'Work', 'Urgent']

def initialize_categories():
        with open(categoriesfile, 'w', newline='') as file:
            writer = csv.writer(file)
            for category in default_categories:
                writer.writerow([category])

def load_tasks():
    tasks = []
    try:
        with open(csvfile, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                tasks.append(row)
    except FileNotFoundError:
        pass
    return tasks

def save_tasks(tasks):
    with open(csvfile, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'title', 'description', 'due_date', 'status', 'category','priority'])
        writer.writeheader()
        for task in tasks:
            writer.writerow(task)

def load_categories():
    categories = []
    try:
        with open(categoriesfile, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:  # Check if the row is not empty
                    categories.append(row[0])  # Append the first column (category name)
    except FileNotFoundError:
        initialize_categories()
        return default_categories
    return categories

def save_category(new_category):
    categories = load_categories()
    if new_category not in categories:
        categories.append(new_category)
        with open(categoriesfile, 'w', newline='') as file:
            writer = csv.writer(file)
            for category in categories:
                writer.writerow([category])

def delete_category_and_update_tasks(category):
    categories = load_categories()
    if category in categories:
        categories.remove(category)
        
        # Update tasks with the deleted category
        tasks = load_tasks()
        for task in tasks:
            if task['category'] == category:
                task['category'] = 'N/A'
        save_tasks(tasks)
        
        # Save updated categories
        with open(categoriesfile, 'w', newline='') as file:
            writer = csv.writer(file)
            for cat in categories:
                writer.writerow([cat])

@app.route('/')
def index():
    tasks = load_tasks()
    categories = load_categories()

    # Filtering tasks by status
    filter_status = request.args.get('filter_status')
    filter_category = request.args.get('filter_category')
    filter_priority = request.args.get('filter_priority')

    if filter_status:
        tasks = [task for task in tasks if task['status'] == filter_status]
    if filter_category:
        tasks = [task for task in tasks if task['category'] == filter_category]
    if filter_priority:
        tasks = [task for task in tasks if task['priority'] == filter_priority]

    return render_template('index.html',
                           tasks=tasks,
                           categories=categories, 
                           selected_status=filter_status,
                           selected_category=filter_category,
                           selected_priority=filter_priority)


@app.route('/add', methods=['GET', 'POST'])
def add_task():
    categories = load_categories()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date = request.form['due_date']
        status = request.form['status']
        category = request.form['category']
        priority = request.form['priority']

        tasks = load_tasks()
        new_task = {
            'id': len(tasks) + 1,
            'title': title,
            'description': description,
            'due_date': due_date,
            'status': status,
            'category': category,
            'priority': priority
        }
        tasks.append(new_task)
        save_tasks(tasks)

        return redirect(url_for('index'))

    return render_template('add_task.html', categories=categories)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    categories = load_categories()
    tasks = load_tasks()
    task = next((t for t in tasks if int(t['id']) == id), None)

    if request.method == 'POST':
        if task:
            task['title'] = request.form['title']
            task['description'] = request.form['description']
            task['due_date'] = request.form['due_date']
            task['status'] = request.form['status']
            task['category'] = request.form['category']
            task['priority'] = request.form['priority']
            save_tasks(tasks)
        return redirect(url_for('index'))

    return render_template('edit_task.html', task=task, categories=categories)

@app.route('/confirm_delete/<int:id>', methods=['GET', 'POST'])
def confirm_delete(id):
    task = next((tsk for tsk in load_tasks() if int(tsk['id']) == id), None)

    if request.method == 'POST' and task:
        tasks = load_tasks()
        updated_tasks = [tsk for tsk in tasks if int(tsk['id']) != id]
        save_tasks(updated_tasks)
        return redirect(url_for('index'))

    return render_template('confirm_task_deletion.html', task=task)

@app.route('/manage_categories', methods=['GET', 'POST'])
def manage_categories():
    categories = load_categories()
    
    if request.method == 'POST':
        if 'add_category' in request.form:
            category_name = request.form.get('category')
            if category_name:
                save_category(category_name)
        
        if 'delete_category' in request.form:
            category_name = request.form.get('category')
            if category_name and category_name in categories:
                delete_category_and_update_tasks(category_name)
        
        return redirect(url_for('manage_categories'))
    
    return render_template('manage_categories.html', categories=categories)

if __name__ == '__main__':
    initialize_categories()
    app.run(debug=True, port=12345)
