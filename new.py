import pandas as pd
import ftfy
df = pd.read_excel('Campaign Data.xlsx')

def fix_mojibake(text):
    if isinstance(text, str):
        try:
            return text.encode("latin1").decode("utf-8")
        except UnicodeError:
            return text  # already fine
    return text

def clean_content_subject_column(df, column="Content_subject"):
    """
    Cleans mojibake / encoding issues in a pandas column.
    Handles emojis, dashes, smart quotes, etc.
    Safe for templated text ({{ ... }}).

    Args:
        df (pd.DataFrame): input dataframe
        column (str): column name to clean

    Returns:
        pd.DataFrame: cleaned dataframe
    """
    from ftfy import fix_text

    def safe_fix(text):
        if not isinstance(text, str):
            return text
        return fix_text(text)

    df[column] = df[column].apply(safe_fix)
    return df

# Apply only where needed
# mask = df["Content_subject"].astype(str).str.contains("ð|Ÿ", na=False)

# df.loc[mask, "Content_subject"] = df.loc[mask, "Content_subject"].apply(fix_mojibake)

df = clean_content_subject_column(df)

print(df[df['Segmentation Logic']=="TGS Shopify - Out for Delivery Audience"].head())
df.to_excel("Campaign_Data_Cleaned.xlsx", index=False)

print("Data cleaning complete. Output saved to Campaign_Data_Cleaned.xlsx")