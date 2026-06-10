export type InstanceStatus = 'DISCONNECTED' | 'QRCODE' | 'CONNECTED';

export interface WhatsappInstance {
  id: string;
  user_id?: string;
  instance_name: string;
  status: InstanceStatus;
  qrcode_base64?: string;
}

export type ChatStatus = 'PENDING' | 'OPEN' | 'CLOSED';

export interface Chat {
  id: string;
  instance_id: string;
  contact_number: string;
  contact_name?: string;
  last_message_preview?: string;
  status: ChatStatus;
  updated_at: string;
}

export type MessageSender = 'CUSTOMER' | 'ATTENDANT' | 'SYSTEM';

export interface Message {
  id: string;
  chat_id: string;
  instance_id: string;
  sender: MessageSender;
  content: string;
  created_at: string;
}
