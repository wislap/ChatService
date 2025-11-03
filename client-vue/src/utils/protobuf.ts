import protobuf from 'protobufjs';

// 解析proto文件并返回根对象
export function loadChatMessageProto(): protobuf.Root {
  // 使用内联方式定义proto内容，避免文件加载问题
  const protoContent = `
    syntax = "proto3";
    package ChatMessageResponse;

    message ChatMessageResponse {
        int32 user_id = 1;
        string username = 2;
        string message_id = 3;
        int32 db_id = 4;
        string content = 5;
        double timestamp = 6;
        string type = 7;
        string alt = 8;
        int32 likes = 9;
        bool liked = 10;
        bool editable = 11;
        bool show_buttons = 12;
        string custom_buttons = 13;
    }

    message MessagesListResponse {
        repeated ChatMessageResponse messages = 1;
        int32 total = 2;
        bool has_more = 3;
    }
  `;

  const parsed = protobuf.parse(protoContent);
  return parsed.root;
}

// 获取消息类型
export function getMessageTypes(root: protobuf.Root) {
  const ChatMessageResponse = root.lookupType('ChatMessageResponse.ChatMessageResponse');
  const MessagesListResponse = root.lookupType('ChatMessageResponse.MessagesListResponse');

  return {
    ChatMessageResponse,
    MessagesListResponse
  };
}

// 将protobuf二进制数据转换为对象
export function decodeMessagesFromProtobuf(protobufData: ArrayBuffer | Uint8Array): Promise<any> {
  return new Promise((resolve, reject) => {
    try {
      const root = loadChatMessageProto();
      const { MessagesListResponse } = getMessageTypes(root);

      // 确保数据是Uint8Array格式
      let uint8Array: Uint8Array;
      if (protobufData instanceof ArrayBuffer) {
        uint8Array = new Uint8Array(protobufData);
      } else {
        uint8Array = protobufData;
      }

      // 解析数据
      const message = MessagesListResponse.decode(uint8Array);

      // 转换为普通对象
      const data = MessagesListResponse.toObject(message, {
        defaults: true,
        arrays: true,
        objects: true
      });

      resolve(data);
    } catch (error) {
      reject(error);
    }
  });
}

// 辅助函数：获取当前用户ID（从localStorage或其他地方）
export function getCurrentUserId(): number {
  // 这里可以根据实际的用户系统返回用户ID
  // 暂时返回0作为示例
  return 0;
}

// 转换protobuf消息格式为组件需要的格式
export function transformProtobufMessages(protobufData: {
  messages: Array<{
    user_id: number;
    username: string;
    message_id: string;
    db_id: number;
    content: string;
    timestamp: number;
    type: string;
    alt: string;
    likes: number;
    liked: boolean;
    editable: boolean;
    show_buttons: boolean;
    custom_buttons: string;
  }>;
  total: number;
  has_more: boolean;
}): {
  messages: Array<{
    id: string;
    sender: string;
    content: string;
    timestamp: Date;
    type: string;
    likes: number;
    liked: boolean;
    editable: boolean;
    showButtons: boolean;
    db_id: number;
    user_id: number;
    alt: string | null;
    customButtons: unknown;
  }>;
  total: number;
  has_more: boolean;
} {
  if (!protobufData.messages || !Array.isArray(protobufData.messages)) {
    return {
      messages: [],
      total: 0,
      has_more: false
    };
  }

  const transformedMessages = protobufData.messages.map((msg: {
    user_id: number;
    username: string;
    message_id: string;
    db_id: number;
    content: string;
    timestamp: number;
    type: string;
    alt: string;
    likes: number;
    liked: boolean;
    editable: boolean;
    show_buttons: boolean;
    custom_buttons: string;
  }) => {
    return {
      id: msg.message_id,
      sender: msg.username,
      content: msg.content,
      timestamp: new Date(msg.timestamp * 1000), // 转换为Date对象
      type: msg.type || 'text',
      likes: msg.likes || 0,
      liked: msg.liked || false,
      editable: msg.editable !== false,
      showButtons: msg.show_buttons !== false,
      db_id: msg.db_id,
      user_id: msg.user_id,
      alt: msg.alt || null,
      customButtons: msg.custom_buttons ? JSON.parse(msg.custom_buttons) : null
    };
  });

  return {
    messages: transformedMessages,
    total: protobufData.total || 0,
    has_more: protobufData.has_more || false
  };
}
