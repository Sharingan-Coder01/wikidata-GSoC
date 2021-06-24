import pandas as pd
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager

def capture(myList):
    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    fileName = "SS/entity"
    ext = ".png"

    for i, f in enumerate(myList):
        driver.get("http://www.google.com/search?q=" + f)
        driver.get_screenshot_as_file(fileName + str(i) + ext)

    driver.quit() 

def main():
    df = pd.read_csv('Uploaded50.csv')
    listn = df.label_bo
    capture(listn)

if __name__ == "__main__":
    main()