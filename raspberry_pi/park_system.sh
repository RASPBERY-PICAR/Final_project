#!/bin/bash  
while inotifywait -e modify /home/pi/Desktop/final_project/state.txt ; do  
	cp /home/pi/Desktop/final_project/CarPicture.jpg /home/pi/Desktop/final_project/CarPictureCopy.jpg        
	curl -F "upload=@/home/pi/Desktop/final_project/CarPictureCopy.jpg" \
	  -F regions=us \
	  -F mmc=false \
	  -F config="{\"mode\":\"fast\"}" \
	  http://localhost:8080/v1/plate-reader/ > /home/pi/Desktop/final_project/LPdata.json      

	python3 /home/pi/Desktop/final_project/get_data.py
done
