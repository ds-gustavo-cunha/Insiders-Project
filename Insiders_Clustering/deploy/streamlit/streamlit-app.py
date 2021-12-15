#######################################
############## LIBRARIES ##############

import inflection
import pandas as pd
import streamlit as st



#######################################
############## FUNCTIONS ##############

# validate data prior to send it to S3 bucket 
class simulate_data_types_pipeline():
    """
    With this class, we will simulate the exact data types transformation
    that will be made at the beginning of the project. 
    
    If this transformations were successful, we can expect no, or at least, 
    less chance of errors in the project pipeline.
    
    So, this class will give us indications about any errors that might be raised 
    in the data processing pipeline before sending the data to the server.
    With this data validation, we can also give the user a chance to correct any incorrect data.
    """

    def __init__(self, csv_file):
        """
        class constructor
        """
        # csv file uploaded by user
        self.original_csv = csv_file
        
        # csv data after transforming into pandas dataframe
        self.csv = None
        
        # flag indicator for the case of errors
        self.error_flag = False

        
    
    def convert_csv_to_pd(self):
        """
        Check if csv convertion to pandas dataframe raises some error.
        """
        
        # convert csv file to pandas dataframe
        self.csv = pd.read_csv( self.original_csv, low_memory = False, encoding = "iso-8859-1", dtype = 'object')

        # check if an 'Unnammed' column was created
        try: # try to drop 'Unnamed' column if it was created
            self.csv.drop( columns = ['Unnamed: 8'], inplace = True )    
        except KeyError: # if 'Unnamed' column was not created
            pass # just continue pipeline
    
    
        return None
    
    
    
    def column_names(self):   
        """
        Check if csv column names are correct.
        """

        # set with expected columnscheck if columns names are correct
        expected_cols = {'InvoiceNo', 'StockCode', 'Description', 'Quantity', 
                         'InvoiceDate', 'UnitPrice', 'Country', 'CustomerID'}
        
        # check if columns names are correct
        {*self.csv.columns} == expected_cols
    
    
        return None

    
    
    def change_columns_case(self):
        """
        Check if column names can be changed to snake case with no errors.
        """
        
        # create a list with column names in snake case
        snake_case = [ inflection.underscore( column ) for column in self.csv.columns ]
        
        # change column names from Pascal case to snake case
        self.csv.columns = snake_case
    
    
        return None

    

    def customer_id(self):
        """
        Check if costomer_id column transformations raise some error.
        """
        
        # remove instance where customer_id is unkown
        self.csv.dropna( axis = 'index', subset = ['customer_id'], inplace = True )

        # conver customer_id to integer dtype
        self.csv['customer_id'] = self.csv['customer_id'].astype( int )
    
    
        return None

    

    def quantity(self):
        """
        Check if quantity column transformations raise some error.
        """       
        
        # conver customer_id to integer dtype
        self.csv['quantity'] = self.csv['quantity'].astype( int )
    
    
        return None

    
    
    def unit_price(self):
        """
        Check if unit_price column transformations raise some error.
        """       
        
        # conver customer_id to integer dtype
        self.csv['unit_price'] = self.csv['unit_price'].astype( float )
    
    
        return None

    
    
    def invoice_date(self):
        """
        Check if invoice_date column transformations raise some error.
        """       

        # convert invoice_date column to date format, instead of string
        self.csv['invoice_date'] = pd.to_datetime( self.csv['invoice_date'], format = '%d-%b-%y' )

        
        return None
        
        
        
    def invoice_no(self):
        """
        Check if invoice_no column transformations raise some error.
        """       
        
        # Remove C letter from invoice numbers,
        # let the quantity as a negative value for these invoices and 
        # convert invoice_no to integer format 
        try:
            self.csv[ 'invoice_no' ] = self.csv[ 'invoice_no' ].str.replace('C', '', regex = False)
            self.csv[ 'invoice_no' ] = self.csv[ 'invoice_no' ].astype( int )
        except AttributeError:
            pass

        
        return None
    


########################################
############## CONSTANTS ###############

# dictionary with data sample
dict_data_sample = {'InvoiceNo': {152959: '549716A', 235108: '557625', 44330: 'T540168', 128100: '547249', 413715: '572318'}, 'StockCode': {152959: '22797C', 235108: '20724R', 44330: '48194', 128100: '85199L', 413715: '23165'}, 'Description': {152959: 'CHEST OF DRAWERS GINGHAM HEART ', 235108: 'RED RETROSPOT CHARLOTTE BAG', 44330: 'DOORMAT HEARTS', 128100: 'LARGE HANGING IVORY & RED WOOD BIRD', 413715: 'LARGE CERAMIC TOP STORAGE JAR'}, 'Quantity': {152959: 1, 235108: 10, 44330: 2, 128100: 1, 413715: 1}, 'InvoiceDate': {152959: '9-Apr-17', 235108: '19-Jun-17', 44330: '3-Jan-17', 128100: '20-Mar-17', 413715: '21-Oct-17'}, 'UnitPrice': {152959: 16.95, 235108: 0.85, 44330: 7.95, 128100: 1.25, 413715: 1.65}, 'CustomerID': {152959: 14628, 235108: 15159, 44330: 13715, 128100: 17832, 413715: 15436}, 'Country': {152959: 'United Kingdom', 235108: 'United Kingdom', 44330: 'United Kingdom', 128100: 'Spain', 413715: 'United Kingdom'}}

# dictionaty with data description
dict_data_description = {'column': {0: 'InvoiceNo', 1: 'StockCode', 2: 'Description', 3: 'Quantity', 4: 'InvoiceDate', 5: 'UnitPrice', 6: 'CustomerID', 7: 'Country'}, 'data type': {0: 'text', 1: 'text', 2: 'object', 3: 'integer', 4: 'text', 5: 'floating-point number', 6: 'integer', 7: 'text'}, 'column description': {0: 'Invoice number (A 6-digit integral number uniquely assigned to each transaction)', 1: 'Product (item) code', 2: 'Product (item) name', 3: 'The quantities of each product (item) per transaction', 4: 'The day when each transaction was generated', 5: 'Unit price (Product price per unit)', 6: 'Customer number (Unique ID assigned to each customer)', 7: 'Country name (The name of the country where each customer resides)'}}

# dictionary with {methods: error message} pair for data validation
methods_and_errors = {'convert_csv_to_pd': 'Error when converting csv to pandas dataframe', 
                      'column_names': 'Please check the column names', 
                      'change_columns_case': 'Error when changing columns case', 
                      'customer_id': 'Please check "CustomerID" column', 
                      'quantity': 'Please check the "Quantity" column', 
                      'unit_price': 'Please check the "UnitPrice" column', 
                      'invoice_date': 'Please check the "invoiceDate" column', 
                      'invoice_no': 'Please check the "InvoiceNO" column'
                      }



###########################################
############## STREAMLIT APP ##############
###########################################


####### LAYOUT INITIALIZATION
# set page layout
st.set_page_config( layout='wide' )

# set title
st.title( 'Streamlit User-Friendly AWS S3 Bucket' )

# create a sidebar so user can check how page works
csv_box = st.sidebar.selectbox(
    label = "Here, you can choose between a good or a bad csv input and we will simulate data insertion so that you can see how this page will work. Try different options to see the results 😉 ...",
    options = ("Good csv input", "Bad csv input", "No csv input") , 
    index = 2
)

# set a caption note
st.caption( 'You can explore the sidebar options by clicking on the upper left side ">" button 🤐 ...' )

# add space between sections
st.text('')


####### DATA QUALITY SECTION
# write a message about importance of data quality
st.markdown("""Hi, you are about to upload data to our data architecture.

Note that, in the best case, machine learning models are as just as good as the data that feed them.
So, **you play a very important role in the performance of our predictions**. 😎 

**Be sure the follow the expected data schema** to help us avoid data processing errors or, even worse, poor predictions.🤝""")

# create check box to show data schema
show_data_schema = st.checkbox('Not sure about the schema? Click here and we will help you ;)')
if show_data_schema:
    # create a dataframe with data description
    df_description = pd.DataFrame(data = dict_data_description)
    # display data description
    st.table( df_description )

    # display message to introduce data sample
    st.write("Check the following example")

    # create a dataframe with an example of data to be uploaded
    df_sample = pd.DataFrame(data = dict_data_sample)
    # display data sample
    st.table( df_sample )

# add space between sections
st.markdown("***")


####### USER INPUT SECTION
# check if user selected the good csv
if csv_box == "Good csv input":
    # set input to data validation
    uploaded_file = "ecommerce_correct.csv"

# check if user selected the bad csv
elif csv_box == "Bad csv input":
    # set input to data validation
    uploaded_file = "ecommerce_wrong.csv"

# check if user select neither good nor bad csv
else:
    # create a button to upload csv files
    uploaded_file = st.file_uploader(label = "Click the button below if you are ready to upload the csv file.",
                                 type = 'csv', 
                                 accept_multiple_files = False,
                                 help = 'Click the "Drag and drop file here" button, select the csv file you want to upload and then click the "open" button on the upper right corner.',
                                 )

# check if a csv file was uploaded
if uploaded_file is not None:
    # instanciate data validator class
    data_validator = simulate_data_types_pipeline( uploaded_file )

    # iterate over data pipeline steps
    for transformation, message in methods_and_errors.items():
        
        try: # try to use the method
            exec(f'data_validator.{transformation}()') # execute method
        
        except BaseException as error: # if method raises an error
            # change error flag to true
            data_validator.error_flag = True
            
            # print message error
            error_message =(f"""Once the data validator indicates an error,\
                            the uploaded csv file can't be sent to our machine learning model 😖.\
                            \n{message} and try again...🤞\
                            \nIf you already checked the uploaded csv file and found no error, \
                            please contact the administrator for further information 👍.""")

    # check if there were errors in data validation
    if data_validator.error_flag:
        # show error message to user
        st.error( error_message )

        # reset data validator
        data_validator = None

    # if validation was successful
    else:
        st.success( """Well done !!! 🤩
        \nThe uploaded csv file was approved by the data validator. 👏
        \nThanks for helping our model make accurate predictions 🤗 ...""")
        
        # reset data_validator
        data_validator = None

# add space between sections
st.text('')
st.text('')
st.text('')
st.markdown("***")


####### DEPLOYMENT ARCHITECTURE SECTION
# create check box to show deployment architecture
# create a message to user
show_data_architecture = st.checkbox("""Do you want to understand your contribution 
                                        to the data architecture? Click here and we will show you 😬...""")

# check if user wants to see architecture
if show_data_architecture:
    # display architecture
    st.image('deployment_architecture.png', use_column_width='auto')

# add space between sections
st.text('')
st.text('')
st.text('')
st.markdown("***")

####### GITHUB LINK SECTION
# create a link so that use can see the github of the project
# print message
st.markdown("""For **further details about** this **project**,
               **click** [here]( https://github.com/ds-gustavo-cunha/Insiders-Project/tree/master/Insiders_Clustering ) 
               and we will help you understand it 😉...""")