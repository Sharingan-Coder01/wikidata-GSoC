import pandas as pd
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager

def capture(myList):
    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    fileName = "SS/entity"
    ext = ".png"

    for i, f in enumerate(myList):
        driver.get("http://www.google.com/search?q=" + f) # Search url with file name 
        driver.get_screenshot_as_file(fileName + str(i) + ext) # Capture screenshot and save

    driver.quit() 

def main():
    df = pd.read_csv('ExtractedData/Rich_Ent_Persons.csv')
    listn = df.label_bo # Name column
    capture(listn)

if __name__ == "__main__":
    main()