import streamlit as st
import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px

#load_dotenv()

st.set_page_config(
     page_title="Voting dApp",
     page_icon="🗳️"
     #layout="wide"
 )


##########################  DEFINE SOME VARAIBLES  ##############################

w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))  # Ganache local provider
accounts = w3.eth.accounts # list of addresses from ganache
proposals_list = ["Proposal 1 - Harm Reduction Program", "Proposal 2 - After School Program", "Proposal 3 - Clean Up"] # List of proposals to display in a dropdown menu
location_list = ["Austin, TX" , "Seattle, WA" , "Denver, CO" , "Philadelphia, PA"] # List of locations to 
registered_voters = [
    "0x31975A1c2353E6f61bfa921387c17330b814Fce9",
    "0x90A987B89217Ff95D3D52f2e51bc6cBE5534be0F",
]

##########################  CONTRACT FUNCTION  ##############################

# Cache the contract on load
@st.cache(allow_output_mutation=True)

# Define the load_contract function
def load_contract():
    # Load Art Gallery ABI
    with open(Path('voterproject_abi.json')) as f:
        certificate_abi = json.load(f)
    # Set the contract address (this is the address of the deployed contract)
    contract_address = "0x2761983f681D9825d6f31d4852502E0Ab9660453"
    # Get the contract
    contract = w3.eth.contract( # functin from web3.py
        address=contract_address, # requires address
        abi=certificate_abi # requires abi
    )
    # Return the contract from the function
    return contract

# Load the contract
contract = load_contract()

##########################  CHARTING FUNCTION  ##############################

def results_graphs():
    
    contract_list = []
    for i in range(len(proposals_list)):
        call = contract.functions.proposals(i).call()
        contract_list.append(call)
    totals_frame = pd.DataFrame(contract_list, columns = ['Proposal','Votes'])

    # Bar Chart - Total Vote by Proposal
    fig = px.bar(x=totals_frame.Proposal, y=totals_frame.Votes, color=totals_frame.Proposal) # title="Votes per Proposal"
    fig.update_yaxes(title="Votes")
    fig.update_xaxes(title="Proposals")

    st.markdown("## Votes per Proposal")
    st.plotly_chart(fig, use_container_width=True)
    #st.write(totals_frame)
    st.write("______________________")


##########################  SUBMIT VOTE FUNCTION  ##############################

def submit_vote(): #callback function executed when submit vote button is pushed
    voted_proposal = proposals_list.index(proposals)    # takes entry from proposal dropdown menu, and finds its index number in the list
    try:
        contract.functions.vote(voted_proposal).transact({'from': account , 'gas': 1000000}) #function with data sent to solidity
        st.success("Thank you, your vote has been submitted.") # message verifying vote was successful
        st.balloons() # freaking balloons!!
    except:
        voted_status = True
        st.error("You cannot vote because you already voted") # error returned if the voter already voted
        st.write(results_graphs())



################################  MAIN BODY  ####################################

st.image("images/dao_or_die_grey.png")
st.image("images/serve_community_blue.png")
st.write("______________________")


##########################  VERIFY ADDRESS  ##############################
st.markdown("### Verify Your Address")
account = st.text_input("Input your wallet address to verify your are eligible to vote")

if st.button("Verify Address"): # button to verify address
    if account in registered_voters: # if statement to see if the text input address is an account in the registered_voters list
        st.write("Your addres has been verified")

##########################  VOTE FUNCTION  ##############################

        with st.form(key = "vote_form"):
            st.markdown("### Vote")
            proposals = st.selectbox("Select a Proposal", options = proposals_list) # displays list of accounts from ganache
            co_op = st.selectbox("Select Your Co-Op", options = location_list)
            if st.form_submit_button("Submit Vote", on_click = submit_vote):
                st.empty()
    else:
        st.error("This wallet address is not eligible to vote.")

##########################  SIDEBAR  ##############################

#IMAGES
st.sidebar.image("images/voting_dapp_image.png")
st.sidebar.title("ABOUT")

with st.sidebar.expander("How to use this Dapp ", expanded=False):
    st.write("STEP 1: In the 'About the Proposals' section below, familiarize yourself with the proposals and choose which one you'd like to vote for.")
    st.write("STEP 2: In the 'Verify your Address' section to the right, enter the verified wallet address you are permitted to vote with.  Click 'Verify Address' ")
    st.write("STEP 3: Once your address is verified the 'Vote' section will appear.  Choose the proposal you want to vote for and the Co-Op you are assocated with.  Then click the 'Vote' button. ")

with st.sidebar.expander("About 'DAO or DIE' ", expanded=False):
    st.write("For its work in the community, DAO or Die has received a grant of $25,000 to spend on a community service project of its choosing.  The DAO members vote to decide how to spend the funds.  See the proposals below.")

with st.sidebar.expander("About the Proposals", expanded=False):
    st.markdown("## About the Proposals")
    proposal_info = st.selectbox("", options = proposals_list)
    if proposal_info == proposals_list[0]:
        st.write("Harm Reduction Project:  Fund overdose prevention programs, syringe access implimentation programs, and expenses for training and capacity facilities.")
    elif proposal_info == proposals_list[1]:
        st.write("After School Program for Low Income Schools: Fund staff for after school activites related to arts, music, and sports.")
    elif proposal_info == proposals_list[2]:
        st.write("Clean Up: Cover expenses to organize and execute a nationwide clean-up initiative across the US")
    else:
        st.empty()


##########################  DATAFRAME  ##############################

# NOTES
# mutual aid netork, network of co-opps, members of DAO, geography based, contributes funds to DAO Treasury
# Vote how to allocate excess treasury funds
# prop 1 - against expenses
# propt 2 - purchase asset (space)
# prop 3 - etc.
