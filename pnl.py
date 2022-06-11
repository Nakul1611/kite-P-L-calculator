import pandas as pd
import numpy as np
import os
import re
import matplotlib.pyplot as plt

#reading orders and calculating charges and PnL
df = pd.read_csv('orders.csv')


df = df[df['Status']!='REJECTED']

df =df[df['Product']!='CNC']
df['Qty.']=df['Qty.'].apply(lambda x: x.split('/')[0])
df['Qty.']=df['Qty.'].astype(int)
df['Total']=df['Avg. price']*df['Qty.']
df['Gross PnL'] = np.where((df['Type']=='BUY'),-1*df['Total'],df['Total'])
df['Charge']=np.minimum(20,(df['Total']*0.03/100))
df['ETC']=df['Total']*0.003/100
df['GST']=df[['Charge','ETC']].sum(axis='columns')*18/100
df['STT']=np.where(df['Type']=='BUY',0,df['Total']*0.025/100)
df['Stamp Duty']=np.where(df['Type']=='BUY',df['Total']*0.003/100,0)
df['Total Charges']=df[['Charge','ETC','GST','STT','Stamp Duty']].sum(axis='columns')
print(df.info())

#df = df[df['Product']!='CNC']
#df_summary is used as intermediate dataframe
df_summary = pd.DataFrame(df.groupby(['Instrument'])['Gross PnL','Total Charges'].sum()).reset_index()
df_summary['Net PnL']=df_summary['Gross PnL']-df_summary['Total Charges']
df_summary['% Charge']=(df_summary['Total Charges']/df_summary['Gross PnL'])*100
df_summary

#df_total is used as intermediate dataframe
df_total = pd.pivot_table(pd.DataFrame(df_summary.sum(axis=0)).reset_index(),columns=['index'],values=[0],aggfunc=lambda x: ' '.join(str(v) for v in x))
df_total['Instrument']='Total'

#df_final is the final summary dataframe
df_final = pd.concat([df_summary,df_total],axis='rows')
list_columns = ['Gross PnL','Total Charges','Net PnL','% Charge']
for i in list_columns:
    df_final[i]=df_final[i].astype(float)
    df_final[i]=df_final[i].round(2)
print(df_final.info())

writer = pd.ExcelWriter('kite_pnl_calculated.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Data', index=False)
df_final.to_excel(writer, sheet_name='Summary', index=False)
writer.save()
df_final