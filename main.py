

import streamlit as st
from tools import read_unread_emails
from agent import agent
from langgraph.types import Command


# ======================== PAGE TITLE ============================
st.title("📧 Email Assistant Agent")


#========================== SESSION STATE ========================

if "unread_emails_list" not in st.session_state:
    st.session_state.unread_emails_list = []

if "current_email_index" not in st.session_state:
    st.session_state.current_email_index = None

if "agent_result" not in st.session_state:
    st.session_state.agent_result = None



#=========================== FETCH EMAILS =======================

if st.button("Read all the Unread Emails"):

    with st.spinner("Connecting to Gmail... Please wait..."):
        st.session_state.unread_emails_list = read_unread_emails()

    # Reset workflow
    st.session_state.current_email_index = None
    st.session_state.agent_result = None

    if isinstance(st.session_state.unread_emails_list, str):
        st.error(st.session_state.unread_emails_list)
        st.session_state.unread_emails_list = []

    elif not st.session_state.unread_emails_list:
        st.info("No unread emails found in your inbox! 🎉")

    else:
        st.success(
            f"Total {len(st.session_state.unread_emails_list)} Email(s) found!"
        )



#======================= SHOW EMAILS =========================

if (
    st.session_state.unread_emails_list
    and st.session_state.current_email_index is None
):

    st.subheader("Unread Emails")

    for email in st.session_state.unread_emails_list:

        with st.expander(
            f"From: {email['from']} | Subject: {email['subject']}"
        ):
            st.write(email["content"])

    st.markdown("---")

    if st.button("Process & Reply Emails"):
        st.session_state.current_email_index = 0
        st.session_state.agent_result = None
        st.rerun()



#======================== PROCESS CURRENT EMAIL =============================

if (
    st.session_state.current_email_index is not None
    and st.session_state.current_email_index
    < len(st.session_state.unread_emails_list)
):

    idx = st.session_state.current_email_index

    email = st.session_state.unread_emails_list[idx]

    st.subheader(
        f"Processing Email {idx + 1} / {len(st.session_state.unread_emails_list)}"
    )

    st.info(
        f"From: {email['from']} | Subject: {email['subject']}"
    )

    config = {
        "configurable": {
            "thread_id": f"email_{email['email_id']}"
        }
    }

   
    #======================= RUN AGENT ONLY ONCE ==========================
  
    if st.session_state.agent_result is None:

        with st.spinner("AI is drafting reply..."):

            inputs = {
                "messages": [
                    (
                        "user",
                        f"""
Read the email from {email['from']}

Subject:
{email['subject']}

Content:
{email['content']}

Draft a simple reply and send it.
"""
                    )
                ]
            }

            st.session_state.agent_result = agent.invoke(
                inputs,
                config=config
            )

    result = st.session_state.agent_result

   
    #=============== HANDLE INTERRUPT ==========================
   
    if "__interrupt__" in result:

        email_body = ""

        try:

            last_msg = result["messages"][-1]

            if (
                hasattr(last_msg, "tool_calls")
                and last_msg.tool_calls
            ):
                email_body = (
                    last_msg.tool_calls[0]
                    .get("args", {})
                    .get("body", "")
                )

        except Exception:
            pass

        editable_body = st.text_area(
            "Generated Reply Body",
            value=email_body,
            height=250
        )

        st.info(
            "Review the reply and choose an action."
        )

        col1, col2, col3 = st.columns(3)

      
        #==================== APPROVE ==============================
    
        with col1:

            if st.button(
                "🟢 Approve",
                use_container_width=True
            ):

                with st.spinner("Sending email..."):

                    agent.invoke(
                        Command(
                            resume={
                                "decisions": [
                                    {
                                        "type": "approve"
                                    }
                                ]
                            }
                        ),
                        config=config
                    )

                st.success("Email sent successfully!")

                st.session_state.current_email_index += 1
                st.session_state.agent_result = None

                st.rerun()

      
        
         #==================== EDIT ==============================
      
        with col2:

            if st.button(
                "✏️ Send Edited Reply",
                use_container_width=True
            ):

                with st.spinner("Sending edited email..."):
                    

                    agent.invoke(
    Command(
        resume={
            "decisions": [
                {
                    "type": "edit",
                    "edited_action": {
                        "name": "send_email",
                        "args": {
                            "to_email": email["from"],
                            "subject": f"Re: {email['subject']}",
                            "body": editable_body
                        }
                    }
                }
            ]
        }
    ),
    config=config
)
                st.success("Edited email sent!")

                st.session_state.current_email_index += 1
                st.session_state.agent_result = None

                st.rerun()

 
        #======================= REJECT ========================
        
        with col3:

            if st.button(
                "❌ Reject",
                use_container_width=True
            ):

                with st.spinner("Rejecting email..."):

                    agent.invoke(
                        Command(
                            resume={
                                "decisions": [
                                    {
                                        "type": "reject"
                                    }
                                ]
                            }
                        ),
                        config=config
                    )

                st.warning("Reply rejected.")

                st.session_state.current_email_index += 1
                st.session_state.agent_result = None

                st.rerun()

    else:
        st.warning(
            "No interrupt received from agent. Check your LangGraph configuration."
        )



#================= ALL EMAILS PROCESSED =============================

if (
    st.session_state.current_email_index is not None
    and st.session_state.current_email_index
    >= len(st.session_state.unread_emails_list)
):

    st.balloons()

    st.success(
        "🎉 All unread emails have been processed successfully!"
    )
    st.info("You can now fetch new emails again.")

    # Reset everything
    st.session_state.unread_emails_list = []
    st.session_state.current_email_index = None
    st.session_state.agent_result = None
