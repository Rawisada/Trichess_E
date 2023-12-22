import random
import websockets
import asyncio
import json

valuepiece = {
     'Pawn': 1, 
     'Knight': 3, 
     'Bishop': 3, 
     'Rook': 5, 
     'Queen': 9, 
     'King': 100
    }

async def ws_client():
    
    url = "ws://192.168.11.20:8181/game"
    # Connect to the server
    #------------------------------------------------------------------------------------------------------
    async with websockets.connect(url) as ws:
        response = await ws.recv()
        json_response = json.loads(response)
        for key, value in json_response.items():
                        print(f"{key} : {value}")
        player = json_response['Player']        #player number
        password = json_response['Password']    #password

        #wait for start
        #--------------------------------------------------------------------------------------------------
        response_Start = await ws.recv()
        json_response_Start = json.loads(response_Start)
        for key, value in json_response_Start.items():
            print(f"{key} : {value}")
        #---------------------------------------------------------------------------------------------------
        while True:  
            try:
                #setting for any turn
                #--------------------------------------------------------------------------------------------
                Mypiece = []            #list of my piece
                board = []              #list of all piece in board
                move_this_turn = []     #list that i will move this turn
                #wait for my turn
                #you will get board here
                #--------------------------------------------------------------------------------------------
                response_MyTurn = await ws.recv()
                response_MyTurn = response_MyTurn.replace("True", "true")
                json_response_MyTurn = json.loads(response_MyTurn)
                # print(f'Received of Myturn : {json.dumps(json_response_MyTurn, indent=2)}')
                #start my turn here
                #--------------------------------------------------------------------------------------------
                if(json_response_MyTurn["YourTurn"] == True):
                    #check all piece in board
                    for piece in json_response_MyTurn['Board']:
                        board.append([piece['Field'], piece['Piece'], piece['Owner']])      #append piece in board
                        # print(f"{piece['Field']}: {piece['Owner']}: {piece['Piece']}")
                    #check my piece
                    #--------------------------------------------------------------------------------------------
                    check_my_piece = {"Command": "MyPiece", "Password": password}
                    await ws.send(json.dumps(check_my_piece, indent=2))
                    response_MyPiece = await ws.recv()
                    json_response_MyPiece = json.loads(response_MyPiece)
                    #append Mypiece
                    for piece in json_response_MyPiece['Board']:
                        Mypiece.append([piece['Field'], piece['Piece']])
                    # print(Mypiece)
                    #---------------------------------------------------------------------------------------------
                    # print('-----------------------Check_Moveable-----------------------')
                    for piece in Mypiece:
                        # print('-----------------------Piece_Moveable-----------------------')
                        # print(piece)
                        this_piece = piece[0]
                        chek_moveable = {"Command": "Movable", "Password": password, "Field": this_piece}
                        await ws.send(json.dumps(chek_moveable, indent=2))           
                        response_MoveAble = await ws.recv()
                        json_response_MoveAble = json.loads(response_MoveAble)
                        # for key, value in json_response_MoveAble.items():
                        #     print(f"{key} : {value}")
                        #can move
                        #------------------------------------------------------------------------------------------
                        if(json_response_MoveAble["Status"] == "Success"):
                            if 'MovableFields' in json_response_MoveAble['Message']:
                                for field_can_move in json_response_MoveAble['MovableFields']:
                                    # print(field_can_move)
                                    #check can x?
                                    #----------------------------------------------------------------------------------
                                    for target in board:
                                        if field_can_move['Field'] == target[0]:    #if it can
                                            #no move in this turn
                                            #--------------------------------------------------------------------------
                                            if len(move_this_turn) == 0:
                                                print(target)        
                                                move_this_turn.append(piece[0])
                                                move_this_turn.append(field_can_move['Field'])
                                                move_this_turn.append(target[1])
                                            #has move already
                                            #--------------------------------------------------------------------------
                                            else:
                                                print('move this turn : ')
                                                print(move_this_turn)
                                                print('target : ')
                                                print(target)                                   
                                                value = target[1]
                                                targetvalue = move_this_turn[2]
                                                print('value : ' + value)
                                                print('targetvalue' + targetvalue)
                                                print('valuepiece[value] :')
                                                print(valuepiece[value])
                                                print('valuepiece[targetvalue] : ')                                            
                                                print(valuepiece[targetvalue])
                                                print('--------------------------')
                                                print(value) # -----------------------
                                                if valuepiece[value] > valuepiece[targetvalue]:   #check priority
                                                    move_this_turn = []             
                                                    move_this_turn.append(piece[0])
                                                    move_this_turn.append(field_can_move['Field'])
                                                    move_this_turn.append(target[1])
                                                else:
                                                    continue
                        #cant move
                        else:  
                            continue
                    #if can x some piece go move
                    #----------------------------------------------------------------------------------------------
                    if len(move_this_turn) != 0:
                        # print(move_this_turn)
                        data_to_send = {"Command": "Move", "Password": password ,"Move": {"From": move_this_turn[0] ,"To": move_this_turn[1]}}
                        await ws.send(json.dumps(data_to_send, indent=2))
                        move_this_turn = []
                        # print(f"Sent: {json.dumps(data_to_send)}")
                        response_after_move = await ws.recv()
                        json_response_after_move = json.loads(response_after_move)
                        #if need promotion
                        #------------------------------------------------------------------------------------------
                        if("RequirePromotion" in response_after_move):
                            # print("-----------------------Promote-----------------------")
                            data_to_send = {"Command": "Promote", "Password": password ,"Promotion":"Queen"}
                            await ws.send(json.dumps(data_to_send, indent=2))
                            # print(f"Sent: {json.dumps(data_to_send)}")
                            response_data = await ws.recv()
                            # print(f'Received of Move : {json.dumps(response_data, indent=2)}')
                            response_data = await ws.recv()
                            # print(f'Received of Move : {json.dumps(response_data, indent=2)}')
                    #if cant x some piece then go random
                    #-----------------------------------------------------------------------------------------------
                    else:
                        print('-----------------------CantX-----------------------')
                        while True:
                            #random piece that move
                            #--------------------------------------------------------------------------------------- 
                            random_piece = random.randint(0, len(Mypiece)-1)
                            # print("-----------------------RandomMyPiece-----------------------")
                            # print(Mypiece[random_piece][0])
                            #check moveable form piece
                            chek_moveable = {"Command": "Movable", "Password": password, "Field": Mypiece[random_piece][0]}
                            await ws.send(json.dumps(chek_moveable, indent=2))
                            response_MoveAble = await ws.recv()
                            json_response_MoveAble = json.loads(response_MoveAble)
                            # for key, value in json_response_MoveAble.items():
                            #     print(f"{key} : {value}")
                            #if it can move
                            #----------------------------------------------------------------------------------------
                            if(json_response_MoveAble["Status"] == "Success"):
                                if 'MovableFields' in json_response_MoveAble['Message']:
                                    random_move = random.randint(0, len(json_response_MoveAble['MovableFields'])-1)
                                    move_this_turn.append(Mypiece[random_piece][0])
                                    move_this_turn.append(json_response_MoveAble['MovableFields'][random_move]['Field'])
                                    # print(move_this_turn)
                                    data_to_send = {"Command": "Move", "Password": password ,"Move": {"From": move_this_turn[0] ,"To": move_this_turn[1]}}
                                    await ws.send(json.dumps(data_to_send, indent=2))
                                    move_this_turn
                                    response_after_move = await ws.recv()
                                    json_response_after_move = json.loads(response_after_move)
                                    if("RequirePromotion" in response_after_move):
                                        print("-----------------------Promote-----------------------")
                                        data_to_send = {"Command": "Promote", "Password": password ,"Promotion":"Queen"}
                                        await ws.send(json.dumps(data_to_send, indent=2))
                                        print(f"Sent: {json.dumps(data_to_send)}")
                                        response_data = await ws.recv()
                                        print(f'Received of Move : {json.dumps(response_data, indent=2)}')
                                        response_data = await ws.recv()
                                        print(f'Received of Move : {json.dumps(response_data, indent=2)}')
                                    break
                        print('---------------------------EndTurn--------------------------------')
                

            except json.JSONDecodeError:
                print('Received non-JSON response')
        
asyncio.get_event_loop().run_until_complete(ws_client())
