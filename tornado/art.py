import os
import lolcat

from random import randint

splash_message = """
 ___      ___  ____  ____  ___  ___________  ______    _______     ______    
|"  \    /"  |("  _||_ " ||"  |("     _   ")/    " \  /" _   "|   /    " \   
 \   \  //   ||   (  ) : |||  | )__/  \\__/// ____  \(: ( \___)  // ____  \  
 /\\  \/.    |(:  |  | . )|:  |    \\_ /  /  /    ) :)\/ \      /  /    ) :) 
|: \.        | \\ \__/ //  \  |___ |.  | (: (____/ // //  \ ___(: (____/ //  
|.  \    /:  | /\\ __ //\ ( \_|:  \\:  |  \        / (:   _(  _|\        /   
|___|\__/|___|(__________) \_______)\__|   \"_____/   \_______)  \"_____/    
                                                                          
"""

def show():
	global splash_message
	print os.getcwd()
	file_list = os.listdir('tornado/ascii')
	choosen_file = file_list[randint(0, len(file_list)-1)]
	print splash_message
	lolcat.run('tornado/ascii/' + choosen_file)
	print "\n\n ============ running web server ============ "