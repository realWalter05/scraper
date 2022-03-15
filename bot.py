from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import csv
import math

# Sets up selenium
chrome_options = Options()
#chrome_options.add_argument("--headless")
s = Service("./Chromedriver/chromedriver.exe")
driver = webdriver.Chrome(service=s, options=chrome_options)

def write_csv(data_list):
    # Create the csv file
    f = open('data.csv', 'w')
    writer = csv.writer(f)        
    
    # Write header row
    header_row = ["Account#","Principal","Owner","Bank Code","Interest","Address","Deductions","Total","City/State","Int.Date","Location","B","L","Q","L.Pay Date","Certificate","Date of Sale","Amount","Subsequents","Type","Status","Lien Holder","Paid_by_0","Paid_by_1","Paid_by_2","Paid_by_3","Paid_by_4","Paid_by_5","Paid_by_6","Paid_by_7","Paid_by_8","Paid_by_9","Paid_by_10","Paid_by_11","Paid_by_12","Paid_by_13","Paid_by_14","Paid_by_15","Paid_by_16","Paid_by_17","Paid_by_18","Paid_by_19"]
    writer.writerow(header_row)

    # Write rows
    for data in data_list:
        writer.writerow(data)
    
    # Close the file
    f.close()    

def get_data(page_source):
    soup = BeautifulSoup(page_source, "html.parser")

    rows = soup.find_all("div", {"class":"row"})
    list_data = []

    first_row_divs = rows[2].find_all("div")
    account = first_row_divs[1].text.strip()
    
    # Splitting blq code if possible
    blq = first_row_divs[3].text.strip().split(" / ")
    b_code = ""
    l_code =  ""
    q_code = ""                
    if len(blq) > 0:
        b_code = blq[0]  
    if len(blq) > 1:
        l_code = blq[1]  
    if len(blq) > 2:
        q_code = blq[2]  

    principal = first_row_divs[5].text.strip()

    second_row_divs = rows[3].find_all("div")
    owner = second_row_divs[1].text.strip()
    bank_code = second_row_divs[3].text.strip().replace("N/A", "")
    interest = second_row_divs[5].text.strip()

    third_row_divs = rows[4].find_all("div")
    address = third_row_divs[1].text.strip()
    deductions = round(float(third_row_divs[3].text.strip()))  
    total = third_row_divs[5].text.strip()  

    fourth_row_divs = rows[5].find_all("div")
    city_state = fourth_row_divs[1].text.strip().replace("  ", " ")    
    int_date = fourth_row_divs[3].text.strip()

    fifth_row_divs = rows[6].find_all("div")
    location = fifth_row_divs[1].text.strip()    
    l_pay_date = fifth_row_divs[3].text.strip()      

    # Getting the paid by data
    paid_bys = []
    table_rows = soup.find("div", {"class": "col-md-7 col-sm-7 col-md-offset-1 col-sm-offset-1"}).find("table").find("tbody").find_all("tr")
    for i in range(1, 20):
        if len(table_rows) > i:
            paid_by = table_rows[i].find_all("td")[9].text.strip()
            paid_bys.append(paid_by)
            continue

        paid_bys.append("")

    certificate = ""
    date_of_sale = ""
    amount = ""
    subsequents = ""
    type_data = ""
    status = ""
    lien_holder = ""
    # Getting the addiotanal values
    if soup.find("tr", {"class": "bred"}):
        print("has certificates")
        add_data_rows = soup.find("div", {"class": "col-md-5 col-sm-5 col-md-offset-1 col-sm-offset-1"}).find("table").find("tbody").find("tr").find_all("td")
        certificate = add_data_rows[0].text.strip()
        date_of_sale = add_data_rows[1].text.strip()
        amount = add_data_rows[2].text.strip()
        subsequents = add_data_rows[3].text.strip()
        type_data = add_data_rows[4].text.strip()
        status = add_data_rows[5].text.strip()
        lien_holder = add_data_rows[6].text.strip()

    data_list = [account, principal, owner, bank_code, interest, address, deductions, total, city_state, int_date, location, b_code, l_code, q_code, l_pay_date, 
                certificate, date_of_sale, amount, subsequents, type_data, status, lien_holder, *paid_bys]
    return data_list      

def get_urls(from_page, to_page):
    urls = []
    def_url = "https://taxes.ci.newark.nj.us"
    for i in range(from_page, to_page):
        url = "https://taxes.ci.newark.nj.us/ViewPay?accountNumber=1"+"{:05d}".format(i)
        urls.append(url)

    return urls

def main():
    # Open the page
    missing_url = []
    data_list = []
    for url in get_urls(1, 200):
        print(url)
        try:
            # Open the browser
            driver.get(url)
            
            # Get the data and store it
            data = get_data(driver.page_source)
            data_list.append(data)

        except Exception as e:
            # Print out the error
            print("some error: " + str(e))
            print("Didn't get: " + url)
            missing_url.append(url)

    write_csv(data_list)
    
    # Close the drive
    driver.close()
    driver.quit()

    print("Data saved")
    print("Didn't get:")
    for missing in missing_url:
        print(missing)

if __name__ == "__main__":
    main()
