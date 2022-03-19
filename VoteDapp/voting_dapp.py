import streamlit as st
import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px

##################  CONFIGURE PAGE ####################

st.set_page_config(page_title = "Voting dApp", page_icon = "🗳️") # add title and emoji to tab in browser

################  INITIALIZE SESSION STATES ################

# PAGES - allows us to control which 'page' the user is on base on the steps they've completed
if 'verified' not in st.session_state:
    st.session_state.verified = False 

if 'voted' not in st.session_state:
    st.session_state.voted = False

if 'view_results' not in st.session_state:
    st.session_state.view_results = False

# THINGS - important variable to remember and recall while using the app
if 'address' not in st.session_state:
    st.session_state.address = "no address"

if 'proposal_index' not in st.session_state:
    st.session_state.proposal_index = 0

if 'balloons_fired' not in st.session_state:
    st.session_state.balloons_fired = False


################ INITIALIZE VARIABLES ################

# Web3 Connection
w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))  # Local connection to Ganache blockchain
accounts = w3.eth.accounts # The active accounts in Ganache session

# Lists
address_list = ["0x273F6c0f8e4C89130AdB1dBC08C16ff3Ce03D9b9" , "0x9591a5Bc34B98d592d0D78d6669ffa3b6923170E" , "0xdb50228409741FE18bAef192420868AEb83484BC" ,  "0x62cA963F0Dcb2f987c373a28f49D43D5326a223D" ,  "0x3c2E96d67A2E6EAA32e283D34568cE7784907648" , "0x8F23BEFC9c6D794615e890E507BA30131262fc76" , "0x2096c99739c76f586886750d2AF1fC8D3157c884" ,  "0x1A6120287801BC7c43a339379a3dfEf6C2a81078" ,  "0x4822E25B8A91EA3CB4578721dD73b703F1c2a01f" ,  "0x4c8295e4dfd6322e822f9Be69533ACa0D3bB3208"]
location_list = ["Austin, TX" , "Philadelphia, PA" , "Denver, CO" , "Seattle, WA"]
proposals_list = ["Proposal 1 - Harm Reduction Program", "Proposal 2 - After School Program", "Proposal 3 - Clean Up"]


##########################  CONTRACT FUNCTION  ##############################

@st.cache(allow_output_mutation=True)  # Cache the contract on load
def load_contract():  # Define the load_contract function
    with open(Path('voting_dapp_abi.json')) as f: # Load ABI so it can talk to remix/contract
        certificate_abi = json.load(f)
    contract_address = "0x6Eb73fD952d7e56650912f295b20F856ab9Fc186"      # Set the contract address (this is the address of the deployed contract)
    contract = w3.eth.contract(  # Get the contract, functin from web3.py
        address=contract_address, # function requires address
        abi=certificate_abi # function requires abi
    )
    return contract # Return the contract from the function

contract = load_contract()  # Load the contract


########################  MAIN BODY HEADER  ###########################

st.image("images/dao_or_die_grey.png")  # Main title image
st.image("images/serve_community_blue.png")  # Subtitle image
st.write("______________________")  # a line


########################  PAGES  ###########################

#  VERIFY ADDRESS - Page 1
if st.session_state.verified == False: # check session state, if session state is false all nested code will be run/displayed
    st.write("### Verify Your Address") # Title
    address = st.text_input("Input your wallet address to verify your are eligible to vote") # Create the variable 'address' and saves the text input from the user in it
    ss_verified = st.button("Verify Address") # Initialize the Verify button
    if ss_verified: # If button pushed, then...
        if address in address_list: # If the address is in the address list, then...
            st.session_state.verified = True # Update verified session state to True
            st.session_state.address = address # save address to session state
            st.experimental_rerun() # Rerun the whole app to guarentee everything displayed is up to date
        else:
            st.error("This wallet address is not eligible to vote.") # error message if your address is not verified

# VOTE - Page 2
elif st.session_state.voted == False:  # check session state, if session state is false all nested code will be run/displayed
    st.write("### Cast Your Vote") # Title
    st.info(f"This address is registered to vote : {st.session_state.address}") # success message displaying the address to the user
    location = st.selectbox("Choose your co-op location", options=location_list) # location drop down menu
    proposal = st.selectbox("Vote for a proposal", options=proposals_list)  # proposal drop down menu
    st.session_state.proposal_index = proposals_list.index(proposal)  # save the list index of the proposal in the session state
    ss_voted = st.button("Vote") # Initialize the Vote button
    if ss_voted:  # If the Vote button is pushed, then...
        st.session_state.voted = True # Update session state for Voted to True
        st.experimental_rerun()  # Rerun the whole app to guarentee everything displayed is up to date

# CONFIRMATION - Page 3
elif st.session_state.view_results == False: # check session state, if session state is false all nested code will be run/displayed
    try: #try the nested block of code.  if the blockchain kicks back an error, move on to 'except'.  This checks to see if the user has already voted
        tx_hash = contract.functions.vote(st.session_state.proposal_index).transact({'from': st.session_state.address, 'gas': 1000000}) #function with data sent to solidity
        b1, c1, b2 = st.columns([1,5,1]) # columns
        with c1: # middle columns
            st.write("## Your vote has been submitted!") # title
            st.image("images/yes.gif") # Zach Galifianakis gif
            st.info(f"Your vote for {proposals_list[st.session_state.proposal_index]} has been submitted") # message displaying which proposal was submitted
            with st.expander("Block Explorer"): # expander container
                tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash) # transactin block data
                st.write(tx_receipt) # display the block data
            st.markdown("#") # spacer
            if st.session_state.balloons_fired == False: # session state of the balloons
                st.balloons() # fire the balloons
                st.session_state.balloons_fired = True # update session state of balloons so they don't fire again

    except:
        if st.session_state.view_results == False:
            b1, c1, b2 = st.columns([1,5,1]) # columns
            with c1: # middle column
                st.write("## You can't vote again") # text
                st.image("images/no.gif") # Danny DeVito gif 
                st.error("Nope. You cannot vote because you already voted.")  # error message
                st.markdown("#") # spacer
        else:
            st.empty()

    b1, c1, b2 = st.columns([1,5,1]) # columns
    with c1: # middle column
        ss_view_results = st.button("View Results") # view results button
        if ss_view_results: # if button is pushed, then...
            st.session_state.view_results = True # set session state to True
            st.experimental_rerun() # rerun the whole app so the display is updated

            

# VIEW RESULTS
else: # check session state, if session state is false all nested code will be run/displayed

    # Button to start over
    start_over_1 = st.button("Start Over")  # a start over button
    if start_over_1:  # if the button is pushed, then....
        st.session_state.voted = False  # update session state to false
        st.session_state.verified = False  # update session state to false
        st.session_state.view_results = False  # update session state to false
        st.experimental_rerun() # rerun the whole app so the display is updated

    # Creating dataframe to display our results
    contract_list = [] #empty list to collect votes
    for i in range(len(proposals_list)): # for loops runs through list of proposals
        call = contract.functions.proposals(i).call() # call solidty contract to retrieve votes that were submitted
        contract_list.append(call)  # append info from solidity to list
    df = pd.DataFrame(contract_list, columns = ['Proposal','Votes']) # convert list into a dataframe

    # Bar Chart - Total Vote by Proposal
    bar_fig = px.bar(x=df.Proposal, y=df.Votes, color=df.Proposal) # initialize the bar graph
    bar_fig.update_yaxes(title="Votes") # y axis title
    bar_fig.update_xaxes(title="") # x axis title
    st.markdown("### Votes per Proposal") # title
    st.plotly_chart(bar_fig, use_container_width=True) # disply the bar graph
    st.write("______________________")  # a line

    # Pie Chart
    pie_fig = px.pie(df, values='Votes', names='Proposal')  # initialize the pie graph
    st.plotly_chart(pie_fig, use_container_width=True) # display the pie graph
    st.write("______________________") # a line
    start_over_2 = st.button(" Start Over ")  # a start over button
    
    # Button to start over
    if start_over_2:  # if the button is pushed, then....
        st.session_state.voted = False  # update session state to false
        st.session_state.verified = False  # update session state to false
        st.session_state.view_results = False  # update session state to false
        st.experimental_rerun() # rerun the whole app so the display is updated



########################  Sidebar ###########################

#IMAGES
st.sidebar.image("images/voting_dapp_image.png")  # title image
st.sidebar.title("ABOUT")  # title

# How to Use this Dapp
with st.sidebar.expander("How to use this Dapp ", expanded=False):
    st.write("STEP 1: In the 'About the Proposals' section below, familiarize yourself with the proposals and choose which one you'd like to vote for.")
    st.write("STEP 2: In the 'Verify your Address' section to the right, enter the verified wallet address you are permitted to vote with.  Click 'Verify Address' ")
    st.write("STEP 3: Once your address is verified the 'Vote' section will appear.  Choose the proposal you want to vote for and the Co-Op you are assocated with.  Then click the 'Vote' button. ")

# About 'DAO or DIE'
with st.sidebar.expander("About 'DAO or DIE' ", expanded=False):
    st.write("For its work in the community, DAO or Die has received a grant of $25,000 to spend on a community service project of its choosing.  The DAO members vote to decide how to spend the funds.  See the proposals below.")

# About the Proposals
with st.sidebar.expander("About the Proposals", expanded=False):
    proposal_info = st.selectbox("", options = proposals_list)
    if proposal_info == proposals_list[0]:
        st.write("### Harm Reduction Project:")
        st.write("Fund overdose prevention programs, syringe access implementation programs, and expenses for training and capacity facilities.")
    elif proposal_info == proposals_list[1]:
        st.write("### After School Programs:")
        st.write("Fund after school programs for Low Income Schools.  This includes staff and supplies for after school activites related to arts, music, and sports.")
    elif proposal_info == proposals_list[2]:
        st.write("### Clean Up:")
        st.write("Fund expenses related to organizing and executing a nationwide clean-up initiative across the US")
    else:
        st.empty()



###### SESSION STATE TRACKER ####### 
# This section displays the status of the various session states which is useful during development)

#st.sidebar.write("# State")
#st.sidebar.write(f"Address Verified: " , st.session_state.verified)
#st.sidebar.write(f"Voted :" , st.session_state.voted)
#st.sidebar.write(f"Address :" , st.session_state.address)
#st.sidebar.write(f"Proposal Index:" , st.session_state.proposal_index)
#st.sidebar.write(f"Viewed Results:" , st.session_state.view_results)
#st.sidebar.write(f"Balloons Fired:" , st.session_state.balloons_fired)


###### OVERIDE BUTTONS ####### 
# This section is a variety of buttons used to navigate the app without outside of the correct way

#st.sidebar.write("# Overide Buttons")
#c1, c2 = st.sidebar.columns(2)

#with c1:
#    ss_verified = st.button("Step 1: True")
#    if ss_verified:
#        st.session_state.verified = True
#        st.experimental_rerun()

#    ss_voted = st.button("Step 2: True")
#    if ss_voted:
#        st.session_state.voted = True
#        st.experimental_rerun()

#    ss_view_results = st.button("View Results: True")
#    if ss_view_results:
#        st.session_state.view_results = True
#        st.experimental_rerun()

#with c2:
#    ss_step1_false = st.button("Step 1: False")
#    if ss_step1_false:
#        st.session_state.verified = False
#        st.experimental_rerun()
    
#    ss_step2_false = st.button("Step 2: False")
#    if ss_step2_false:
#        st.session_state.voted = False
#        st.experimental_rerun()









# see_the_code = st.button("See the code")
#if see_the_code:
#    with st.echo():
#        import time
#        my_bar = st.progress(0)
#
#        for percent_complete in range(100):
#            time.sleep(0.01)
#            my_bar.progress(percent_complete + 1)













