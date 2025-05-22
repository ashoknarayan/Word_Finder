# 🐾 Word Finder Game with Positional Index 🐾

A fun and fast **Python + Pygame** app that helps you guess words from partial letter inputs!  
Just enter the word length, fill in known letters, and get a list of possible matches from a huge dictionary — all powered by a clever positional bitmask index. ⚡️

---

## 🚀 Features

- Enter word length (1–20)  
- Fill known letters in interactive boxes (or leave blanks)  
- Lightning-fast word lookup using bitmask filtering  
- Scrollable list of matching words  
- Play Again button to restart anytime

---

## 🛠️ Setup & Run

1. Install Python 3 and Pygame:  
   `pip install pygame`

2. Make sure your `pos_index.json` (built from your word list using `build.py`) is in the same folder.

3. Run the game:  
   `python main.py`

---

## 🎮 How To Play

- Input the length of the word you want to find.  
- Type known letters into the boxes (use arrow keys to move, backspace to clear).  
- Press Enter to see all possible matches.  
- Scroll with mouse wheel if results overflow.  
- Click Play Again to try another word!

---

## 📚 How It Works

We pre-build a positional index from a word list, storing bitmasks for each letter at each position. This lets us quickly filter out impossible words by intersecting bitmasks, making the search blazing fast!

---
- Please run the build.py on a [words.txt](https://github.com/dwyl/english-words/blob/master/words.txt) file. Then play with the main.py
Made with ❤️ by Ashok Narayan | Happy guessing! 🎉
