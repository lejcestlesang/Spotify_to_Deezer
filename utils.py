

def wanna_saved(tipo,df):
    """ASk the user to save the df """
    saved= input(f'Want to save {tipo} to a file ? (y/n) :')
    if saved == 'y':
        df.to_excel(f'Data/{tipo}.xlsx')
        print(f'{tipo} from saved to an excel file')