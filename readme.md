# GeoBERT text classification
**ქართულენოვანი BERT multi-class ტექსტური კლასიფიკაციის მოდელი HuggingFace და Simple Transformers-ის დახმარებით.**

## სარჩევი

1. [**შესავალი**](#შესავალი)

## შესავალი

ინტერნეტში არსებული ტუტორიალების და პოსტების უმრავლესობა გვასწავლის როგორ გამოვიყენოთ BERT-ის  არქიტექტურაზე დაფუძნებული ინგლისურ ენოვანი ტექსტის კლასიფიკაციის, სენტიმენტ ანალიზის, კითხვა-პასუხის ან ტექსტის გენერატორი მოდელები. ჩემი ამოცანაა შევძლო ქართულ ენაზე მსგავსი ოპერაციების ჩატარება და ვიწყებ ტექსტის კლასიფიკაციის მოდელით.

> ! გადათარგმნე ინგლისურად ! 

I'll be using this repository to track my progress and version control my work. 

You will find main tools and/or instructions needed to reproduce the solutions on your hardware.

## Instructions

Clone the repository and navigate to GeoBERT with `cd GeoBERT`

You need to install all the requirements needed to run the program. run:

```commandline
pip install -r requirements.txt
```

### Corpus Toolset demo
navigate to GNLP toolset:
```commandline
cd GNLP
python corpus.py
```

> დავამატებ დეტალურ ინსტრუქციას და გარჩევას toolset-ის დოკუმენტირებისას როცა ამის დრო მექნება

### Web Service Demo
```commandline
cd SpellCheck
python spell.py
```

## რესურსები
1. [GitHub: google-research_BERT](https://github.com/google-research/bert)
2. [NLP Models Tensorflow](https://github.com/huseinzol05/NLP-Models-Tensorflow/tree/master/spelling-correction)
3. [How to train a new language model from scratch using Transformers and Tokenizers](https://huggingface.co/blog/how-to-train)
4. [Transformer: A Novel Neural Network Architecture for Language Understanding](https://ai.googleblog.com/2017/08/transformer-novel-neural-network.html)
5. https://www.freecodecamp.org/news/google-bert-nlp-machine-learning-tutorial/
6. https://towardsdatascience.com/bert-text-classification-in-a-different-language-6af54930f9cb
7. http://norvig.com/spell-correct.html
