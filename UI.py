import tkinter as tk
from tkinter import scrolledtext, messagebox
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import ujson
import webbrowser

# Initialize GUI
window = tk.Tk()
window.title("Article Search Engine")
window.geometry('1150x700')
window.configure(bg='white')

# Load data and models
with open('pub_list_stemmed.json', 'r') as file:
    pub_list_first_stem = ujson.load(file)
with open('pub_indexed_dictionary.json', 'r') as file:
    pub_index = ujson.load(file)
with open('pub_name.json', 'r') as file:
    pub_name = ujson.load(file)
with open('pub_url.json', 'r') as file:
    pub_url = ujson.load(file)
with open('pub_cu_author.json', 'r') as file:
    pub_cu_author = ujson.load(file)
with open('pub_date.json', 'r') as file:
    pub_date = ujson.load(file)

# Initialize NLTK components
stemmer = PorterStemmer()
stop_words = stopwords.words('english')
tfidf = TfidfVectorizer()

# Function to perform publication search
def pub_qp_data():
    outputData.delete('1.0', tk.END)
    inputText = inputBar.get()
    abc = {}

    if operator.get() == 1:  # AND operator
        outputData.configure(fg='black')
        inputText = inputText.lower().split()
        pointer = []
        for token in inputText:
            if len(inputText) < 2:
                messagebox.showinfo(title="Attention!!!", message="Try with more character")
                break
            if len(token) <= 3:
                messagebox.showinfo("Error!!!", "Try again with more characters.")
                break
            stem_temp = ""
            stem_word_file = []
            temp_file = []
            word_list = word_tokenize(token)

            for x in word_list:
                if x not in stop_words:
                    stem_temp += stemmer.stem(x) + " "
            stem_word_file.append(stem_temp)
            if pub_index.get(stem_word_file[0].strip()):
                pointer = pub_index.get(stem_word_file[0].strip())
            else:
                if len(inputText) == 1:
                    pointer = []

            if len(pointer) == 0:
                abc = {}
            else:
                for j in pointer:
                    temp_file.append(pub_list_first_stem[j])
                temp_file = tfidf.fit_transform(temp_file)
                cosine_output = cosine_similarity(temp_file, tfidf.transform(stem_word_file))

                if pub_index.get(stem_word_file[0].strip()):
                    for j in pointer:
                        abc[j] = cosine_output[pointer.index(j)]

    elif operator.get() == 2:  # OR operator
        outputData.configure(fg='black')
        inputText = inputText.lower().split()
        pointer = []
        for token in inputText:
            if len(token) <= 3:
                messagebox.showinfo("Error!!!", "Please enter more than 4 characters.")
                break
            stem_temp = ""
            stem_word_file = []
            temp_file = []
            word_list = word_tokenize(token)

            for x in word_list:
                if x not in stop_words:
                    stem_temp += stemmer.stem(x) + " "
            stem_word_file.append(stem_temp)
            if pub_index.get(stem_word_file[0].strip()):
                pointer.extend(pub_index.get(stem_word_file[0].strip()))

        if len(pointer) == 0:
            abc = {}
        else:
            for j in pointer:
                temp_file.append(pub_list_first_stem[j])
            temp_file = tfidf.fit_transform(temp_file)
            cosine_output = cosine_similarity(temp_file, tfidf.transform(inputText))

            if pub_index.get(stem_word_file[0].strip()):
                for j in pointer:
                    abc[j] = cosine_output[pointer.index(j)]

    aa = 0
    for a in sorted(abc, key=abc.get, reverse=True)[:10]:
        outputData.insert(tk.INSERT, 'Article Title: ' + pub_name[a] + "\n")
        outputData.insert(tk.INSERT, 'URL: ' + pub_url[a] + "\n")
        outputData.insert(tk.INSERT, 'Published Date: ' + pub_date[a] + "\n")
        outputData.insert(tk.INSERT, 'Related Author: ' + pub_cu_author[a] + "\n")
        outputData.insert(tk.INSERT, "\n")
        aa += 1

    if aa == 0:
        messagebox.showinfo("Error!!!", "Please try again with suitable keywords.")

# Function to handle hyperlink redirection
def browse_url(event):
    widget = event.widget
    index = widget.index("@%s,%s" % (event.x, event.y))
    url = widget.get(index)
    if url.startswith('URL: '):
        url = url[5:]
    webbrowser.open(url)

# GUI elements
label = tk.Label(window, text="Article Search Engine", bg="#439A97", fg="white", font="Arial 24 bold")
label.pack(pady=20)

inputBar = tk.Entry(window, width=55, bg="white")
inputBar.pack()

operator = tk.IntVar()
operator.set(1) 

rb_and = tk.Radiobutton(window, text='Relevant Match', bg="#577D86", fg="white", value=1, variable=operator, font="Arial 12 bold")
rb_and.pack()

search = tk.Button(window, text='SEARCH', bg="#577D86", fg="black", font="Arial 10 bold", command=pub_qp_data)
search.pack(pady=10)

outputData = scrolledtext.ScrolledText(window, width=130, height=35, bg="white")
outputData.pack(pady=20)
outputData.tag_config('link', foreground='blue', underline=True)
outputData.bind("<Button-1>", browse_url)

# Run the GUI
window.mainloop()
