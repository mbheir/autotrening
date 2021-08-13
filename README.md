# Autotrening.sexy

A booking subscription service for training centers in Trondheim. 

## Description
During covid, most training centers in Trondheim were completely overbooked due to hard limits on the number of people that were allowed to train simultaneously.
The sessions were available on the booking system 48 hours in advance, but were full in a matter of seconds. As a result, you'd have to be ready 48 hours before every occation, and you'd still have no guarantee of a spot. Thus, a solution had to be made. 

The Autotrening.sexy service would let you set up a subscription of a few sessions per week through a website, and then it would automatically book you to the specified sessions. The subscription would go on until changed or cancelled. 

## Booking page
<p align="center">
<img width="546" alt="Screenshot 2021-08-13 at 09 56 59" src="https://user-images.githubusercontent.com/55540484/129324883-c445486f-cf46-4e1c-a053-4a2e8c716c58.png">
</p>

## Status page
<p align="center">
<img width="546" alt="Screenshot 2021-08-13 at 09 56 59" src="https://user-images.githubusercontent.com/55540484/129337821-dfe15d3b-0f84-497f-ade1-9ac1c8deab51.png">
</p>


## How it works
The user fills out a form on the website and presses submit. A http post request is then sent to the backend python server. The entries is then written to a simple database. Another thread is periodically waking up from sleep to perform concurrent booking of the selected entries in the database. It parses the booking website for a key to the specific session and sends concurrent http post requests to perform the accreditation and the booking. 
