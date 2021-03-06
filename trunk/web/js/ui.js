Ext.BLANK_IMAGE_URL = "extjs/resources/images/default/s.gif"

Ext.namespace('yakalope');
  
yakalope.app = function () {
  var viewport;
  var username;
  var openChats;
  return {
    getViewport: function() {
      return viewport;
    },
    getChatArea: function () {
      return viewport.items.get('chatarea');
    },
    getBuddyList: function() {
      return viewport.items.get('buddylist');
    },
	getLogWin: function() {
      return viewport.items.get('logwin');
    },
    init: function() {
      if (jabber.isConnected() == false) {
        Login.login();
      }         
      jabber.init();
      this.openChats = new Array();
      /* Setup Layout of Main Window */
  
      viewport = new Ext.Viewport({
      layout: 'border',
      items:
      [{ 
        /* Chat Area */
        
        xtype:'panel',
        region:'center',
        margins:'10 0 0 0',
        id:'chatarea',
        key:'chatarea',
        dd:true,
        autoScroll:true,
       
        /* End Chat Area */
      
      },{
           
        /* Buddy Window */
        
        region:'east',
        id:'buddylist',
        title:'Buddy List',
        margins:'10 0 0 0',
        cmargins: '10 0 0 0',
        xtype:'buddylist'

        /* End Buddy Window */ 

      },{
           
        /* Search */
      
        region:'west',
        id:'logwin',
        title:'Search',
        margins:'10 0 0 0',
        cmargins: '10 0 0 0',
        xtype:'logwin'

        /* End Search */ 

      }]
      
      /* End Main Layout */

      });
    },
    getUserName: function() {
      return this.username;
    },
    setUserName: function(userName) {
      this.username = userName;
    },
    createNewChatWindow: function(chatId) {
      if (!Ext.get(chatId)) {
        //var chatArea = yakalope.app.getChatArea();
        var newChat = new ChatWindow({
          id:chatId,
          title:chatId,
          hidden:false,
          key:chatId,
          user:this.getUserName(),
        });
        this.openChats.push(chatId);
        newChat.show(this);
        return newChat;
      }
      return null;
    },
    removeChatWindow: function(chatId) {
      Ext.getCmp(chatId).close();
      this.openChats.remove(chatId);
    },
    addMsg: function(chatId, msg) {
      var chatWindow = Ext.getCmp(chatId);
      if (chatWindow) {
        chatWindow.addMsg(chatId, msg);
      } else {
        var newChatWindow = yakalope.app.createNewChatWindow(chatId);
        newChatWindow.addMsg(chatId, msg);
      }
    },
    subscribeBuddy: function(username, domain) {
      var user = username + '@' + domain;
      jabber.subscribe(user);
    },
    unsubscribeBuddy: function(username, domain){
      var user = username + '@' + domain;
      jabber.unsubscribe(user);
    },
    clearChatWindows: function() {
      var arrlength = this.openChats.length;
      var i = 0;
      for (; i < arrlength; i++) {
        var chatId = this.openChats[i];
        this.removeChatWindow(chatId);
      }
      this.openChats = new Array();
    }
  }
}();

Ext.onReady(yakalope.app.init, yakalope.app);
