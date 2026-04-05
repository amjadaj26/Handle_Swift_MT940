import re
import pandas as pd
def parse_multi_account_mt940():
    with open("Your_Source", 'r') as f:
        content = f.read()
    statement_blocks = re.split(r'\n-}\n',content)
    #print(statement_blocks)
    all_data=[]
    for block in statement_blocks:
        if not block.strip():
            continue
        #Start extracting all the data for each block
        tag60F_pattern = r":60F:(C|D)(\d{6})([A-Z]{3})([0-9,]+)"
        tag62F_pattern = r":62F:(C|D)(\d{6})([A-Z]{3})([0-9,]+)"
        Statement_ref = re.search(r":20:(.*)",block).group(1)
        Account_no = re.search(r":25:(.*)",block).group(1)
        Opening_Bal = re.search(tag60F_pattern, block).group(4).replace(',','.')
        Opening_Bal_Date = re.search(tag60F_pattern, block).group(2)
        Closing_Bal = re.search(tag62F_pattern, block).group(4).replace(',','.')
        Closing_Bal_Date = re.search(tag62F_pattern, block).group(2)
        Currency = re.search(tag60F_pattern, block).group(3)
        #print(Statement_ref)
        #Extracting the tag 61
        # tag61 = re.findall(r":61:(.*)",block)
        tx_pattern =re.compile(r':61:(.*?)(?=:61:|:62F|:62M|$)', re.DOTALL)
        transactions = tx_pattern.findall(block)
        for transaction in transactions:
            # Groups: 1:ValDate, 2:EntryDate, 3:DC, 4:Fund, 5:Amount, 6:TxType, 7:CustRef, 8:BankRef
            tran = re.search(r'^(\d{6})(\d{4})?([DRC])([a-zA-Z])?([\d,]+)([a-zA-Z0-9]{4})([^/]+)?(?://([^\n]+))?', transaction)
            Description = re.search(r':86:(.*)', transaction)
            # print(transactions)
            if tran:
                all_data.append({
                    'Statement_Ref':Statement_ref,
                    'Account_No':Account_no,
                    'Currency':Currency,
                    'Value_Date':tran.group(1),
                    'Entry_Date':tran.group(2),
                    'Debit/Credit': tran.group(3),
                    'Amount':tran.group(5).replace(',','.'),
                    'Trans_Type':tran.group(6),
                    'Cust_Ref':tran.group(7),
                    'Bank_Ref':tran.group(8),
                    'Opening_Bal':Opening_Bal,
                    'Closing_Bal':Closing_Bal,
                    'Closing_Bal_Date':Closing_Bal_Date,
                    'Opening_Bal_Date':Opening_Bal_Date,
                    'Description':Description.group(1)
                }) 
    return pd.DataFrame(all_data)
