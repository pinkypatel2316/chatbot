from flask import Flask, render_template, request, url_for, jsonify, send_file, redirect
import csv
from chat import get_response
import io
import json

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("base.html")


chat_history = []

unresolved_queries = []

UNRESOLVED_QUERIES_CSV = 'templates/unresolved_queries.csv'
@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    
    response = get_response(text)
    chat_history.append({"user_input": text, "chatbot_response": response}) 
    if response == "I do not understand...":
        append_to_unresolved_queries(text)
  
    message = {"answer": response}
    return jsonify(message)



@app.route("/export_chat_history")
def export_chat_history():
    # Create CSV data
    csv_data = io.StringIO()
    fieldnames = ["query", "response"]
    writer = csv.DictWriter(csv_data, fieldnames=fieldnames)
    writer.writeheader()
    
    # Write chat history data to CSV
    for chat in chat_history:
        writer.writerow({field: chat.get(field, "") for field in fieldnames})

    # Serve CSV file as a download
    csv_data.seek(0)
    return send_file(
        csv_data,
        mimetype="text/csv",
        as_attachment=True,
        download_name="chat_history.csv"
    )




def load_intents():
    with open('intents.json', 'r') as json_file:
        intents = json.load(json_file)
    return intents


def save_intents(intents):
    with open('intents.json', 'w') as json_file:
        json.dump(intents, json_file, indent=4)


def save_resolved_query(query):
    with open('templates/resolved_queries.csv', 'a', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=['query', 'response'])
        writer.writerow(query)


@app.route('/')
def user_interface():
    file_path = 'templates/unresolved_queries.csv'  # Path relative to the templates folder
    unresolved_queries = read_csv_file(file_path)
    return render_template('user_interface.html', unresolved_queries=unresolved_queries)

@app.route('/delete/<query_id>')
def delete_query(query_id):
    file_path = 'templates/unresolved_queries.csv'  # Path relative to the templates folder
    # Your code to delete the query with the given ID
    return redirect(url_for('user_interface'))  # Redirect back to the user interface page



def delete_unresolved_query(query_id):
    unresolved_queries = load_unresolved_queries()
    with open('templates/resolved_queries.csv', 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=['query_id', 'query'])
        writer.writeheader()
        for query in unresolved_queries:
            if query['query_id'] != query_id:
                writer.writerow(query)


def mark_query_resolved(query_id, response):
    # Load unresolved queries
    unresolved_queries = load_unresolved_queries()
    # Find the query with the given query_id
    for query in unresolved_queries:
        if query['query_id'] == query_id:
            resolved_query = {'query': query['query'], 'response': response}
            # Save resolved query to CSV file
            save_resolved_query(resolved_query)
            # Update intents.json with the new query-response pair
            intents = load_intents()
            intents['intents'].append({'tag': query['query'], 'patterns': [query['query']], 'responses': [response]})
            save_intents(intents)
            # Delete the query from unresolved queries CSV file
            delete_unresolved_query(query_id)
            break





def append_to_unresolved_queries(query):
   
    with open(UNRESOLVED_QUERIES_CSV, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([query])


@app.route("/export_csv")
def export_csv():
    # Generate CSV data from chat history
    csv_data = io.StringIO()
    writer = csv.DictWriter(csv_data, fieldnames=["user_input", "chatbot_response"])
    writer.writeheader()
    writer.writerows(chat_history)

    # Serve CSV file as a download
    return send_file(
        io.BytesIO(csv_data.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="chat_history.csv"
    )

@app.route("/templates/unresolved_queries")
def get_unresolved_queries():
    # Prompt message for admin
    prompt_message = "Please review the unresolved queries and add responses."

    # Return unresolved queries and prompt message
    return jsonify({"unresolved_queries": unresolved_queries, "prompt_message": prompt_message})




@app.route("/admin")
def admin_interface():
    questions = []
    with open('./templates/unresolved_queries.csv', 'r') as file:
        csv_reader = csv.reader(file)
        i=1
        for row in csv_reader:
            row.insert(0,i)
            i+=1
            questions.append(row)
    return render_template("admin_interface.html",unresolved_queries=unresolved_queries,questions = questions)

@app.route("/admin/add_response", methods=["POST"])
def add_response():
    tag = request.form.get("tag")
    response = request.form.get("response")
    id = request.form.get("id")
    question=request.form.get("question")
   
    
    with open('intents.json', 'r') as file:
        data = json.load(file)

   
    intents = data['intents']

    # Step 3: Search for the particular tag
    tag_to_search = tag
    tag_found = False
    for intent in intents:
        if intent['tag'] == tag_to_search:
            # Step 4: Append the question string to the patterns list
            intent['patterns'].append(question)

            # Step 4: Append the response string to the responses list
            intent['responses'].append(response)
            tag_found = True
            break

    # Step 5: If the tag is not present, add a new object to the intents list
    if not tag_found:
        new_intent = {
            'tag': tag_to_search,
            'patterns': [question], 
            'responses': [response] 
        }
        intents.append(new_intent)

    # Step 6: Convert the modified Python dictionary back to JSON format
    updated_data = {'intents': intents}
    updated_json = json.dumps(updated_data, indent=4)

    # Step 7: Write the updated JSON data back to the file
    with open('intents.json', 'w') as file:
        file.write(updated_json)

    #step8 remove the id question from csv file
    with open(UNRESOLVED_QUERIES_CSV, 'r', newline='') as file:
        lines = file.readlines()

    # Remove the line with the specified query ID
    if 1 <= int(id) <= len(lines):
        del lines[int(id) - 1]

    # Write the updated contents back to the CSV file
    with open(UNRESOLVED_QUERIES_CSV, 'w', newline='') as file:
        file.writelines(lines)

    return redirect(url_for('admin'))



def read_csv_file(file_path):
    data_list = []
    with open(file_path, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            data_list.append(row)
    return data_list



def write_csv_file(file_path, data):
    with open(file_path, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(data)

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        question_id = request.form['question_id']
        answer = request.form['answer']
        response = [question_id, answer]

        # Remove the answered question from the CSV file
        file_path = './templates/unresolved_queries.csv'
        with open(file_path, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            data = list(csv_reader)
            for row in data:
                if row[0] == question_id:
                    data.remove(row)
                    break

        # Write updated data back to CSV file
        write_csv_file(file_path, data)

        # Append response to CSV file
        response_file_path = 'responses.csv'
        with open(response_file_path, 'a', newline='') as response_file:
            csv_writer = csv.writer(response_file)
            csv_writer.writerow(response)

        return redirect('admin')


# @app.route("/chat_history")
# def chat_history():
#     chat_data = read_chat_history()  
#     return render_template("chat_history.html", chat_data=chat_data)



# def read_chat_history():
#     chat_data = []
#     with open('chat_history.csv', 'r') as file:
#         reader = csv.reader(file)
#         for row in reader:
#             chat_data.append({
#                 'timestamp': row[0],
#                 'user_input': row[1],
#                 'chatbot_response': row[2]
#             })
#     return chat_data



if __name__ == "__main__":
    app.run(debug=True)
