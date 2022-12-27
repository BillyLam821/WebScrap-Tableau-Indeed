import numpy as np
import pandas as pd
from datetime import date

# read web scrapped data
today = str(date.today())
df = pd.read_json(f"indeed_{str(today)}.json")

# read skillset file for mapping
# separating in another file for flexible addition / removal
with open("skillset.txt", "r") as f:
    skillset = f.read().split("\n")
    f.close()

# flatten description lists and turn them into lower case
df["description"] = df["description"].apply(lambda x: ",".join(x).lower())

# create an empty table for skill dimension
dim_df = pd.DataFrame(columns=["job_id", "skill"])

# populate job id and skill to dimension table if description contains skills
for skill in skillset:
    update_id = df.index[df["description"].str.contains(skill)]
    df.loc[update_id, "skill"] = skill.title()
    dim_df = pd.concat([dim_df, df.loc[update_id, ["job_id", "skill"]]], ignore_index=True)

dim_df.loc[dim_df['skill'].str.contains("\+"), "skill"] = "C++"
df.drop(["skill"], axis=1, inplace=True)

# one-hot encoding the skills if not using dimension table
# skill_df = pd.DataFrame(0, index=np.arange(len(df)), columns=skillset)
# df = pd.concat([df, skill_df], axis=1)

# mark skills as 1 if job description contains
# for skill in skillset:
#     update_id = df.index[df["description"].str.contains(skill)]
#     df.loc[update_id, skill] = 1

df.drop(["description"], axis=1, inplace=True)
df.to_excel(f"indeedFact_{today}.xlsx", index=False)
dim_df.to_excel(f"indeedDim_{today}.xlsx", index=False)
print("Records saved successfully.")