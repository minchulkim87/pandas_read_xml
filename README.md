# Pandas Read XML

A tool to help read XML files as pandas dataframes.

See example in [Google Colab here](https://colab.research.google.com/github/minchulkim87/pandas_read_xml/blob/master/pandas_read_xml_example.ipynb)

Isn't it annoying working with data in XML format? I think so. Take a look at this simple example.

```xml
<first-tag>
    <not-interested>
        blah blah
    </not-interested>
    <second-tag>
        <the-tag-you-want-as-root>
            <row>
                <columnA>
                    The data that you want
                </columnA>
                <columnB>
                    More data that you want
                </columnB>
            </row>
            <row>
                <columnA>
                    Yet more data that you want
                </columnA>
                <columnB>
                    Eh, get this data too
                </columnB>
            </row>
        </the-tag-you-want-as-root>
    </second-tag>
    <another-irrelevant-tag>
        some other info that you do not want
    </another-irrelevant-tag>
</first-tag>
```

I wish there was a simple `df = pd.read_xml('some_file.xml')` like `pd.read_csv()` and `pd.read_json()` that we all love.

I can't solve this with my time and skills, but perhaps this package will help get you started.


## Install

```bash
pip install pandas_read_xml
```

## Import package

```python
import pandas_read_xml as pdx
```

## Read XML as pandas dataframe

You will need to identify the path to the "root" tag in the XML from which you want to extract the data.

```python
df = pdx.read_xml("test.xml", ['first-tag', 'second-tag', 'the-tag-you-want-as-root'])
```

*Sometimes, the XML structure is such that pandas will treat rows vs columns in a way that we think are opposites. For these cases, the read_xml may fail. Try using `transpose=True` as an argument in such cases.

# Auto Flatten

The real cumbersome part of working with XML data (or JSON data) is that they do not represent a single table. Rather, they are a (nested) tree representations of what probably were relational databases. Often, these XML data are exported without a clearly documented schema, and more often, no clear way of navigating the data.

What is even more annoying is that, in comparison to JSON, the data structures are not consistent across XML files from the same schema. Some files may have multiples of the same tag, resulting in a list-type data, while in other files of the *same* schema will only have on of that tag, resulting in a non-list-type data. In other times, the tags are not present which means that the resulting "column" is not just null, but not even a column. This makes it difficult to "flatten".

Pandas already has some tools to help "explode" (items in list become separate rows) and "normalise" (key, value pairs in one column become separate columns of data), but they fail when there are these mixed types within the same tags (columns). Besides, "flattening" (combining exploding and normalising) duplicates other data in the dataframe as well, leading to an explosion of memory requirements.

So, in this tool, I have also attempted to make a few different tools to separate the relational tables.

See the example in Colab (or run the notebook elsewhere)

The `auto_separate_tables` method will separate out what it guesses to be separate tables. The resulting `data` is a dictionary where the keys are the "table names" and the corresponding values are the pandas dataframes. Each of the separate tables will have the `key_columns` as common columns.

You can see the list of separated tables by using python dictionary methods.

```python
data.keys()
```

And then view the table of interest.

There are also other "smaller" functions that does parts of the job:

- flatten(df)
- auto_flatten(df, key_columns)
- fully_flatten(df, key_columns)

Even more if you look through the code.
