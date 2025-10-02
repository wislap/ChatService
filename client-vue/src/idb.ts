import { openDB, deleteDB } from 'idb'

// Database name and version

/**
 * Initialize the database by opening or creating it
 */
export const initializeDB = async (): Promise<void> => {
  try {
    const db = await openDB("ChatMessages", 1, {
      upgrade(db) {
        // Create object store for chat messages
        db.createObjectStore('GaMessages')
      }
    })
    console.log('Database opened successfully')
    db.close()
  } catch (error) {
    console.error('Error opening database:', error)
  }
}

export const test = async (): Promise<void> => {
  let placeholderMessages = [
    "Hi there! How are you today?",
    "I'm doing well, thank you for asking.",
    "This chat interface has an adjustable message area.",
    "You can type messages in the input below and click send.",
    "You can type messages in the input below and click send.",
  ]
  let i:number;

  for(i=0;i<2;i++){
    placeholderMessages = placeholderMessages.concat(placeholderMessages)
  }

  try {
    const db = await openDB("ChatMessages", 1)
    let index:number;
    for(index=0;index<placeholderMessages.length;index++){
      const message = placeholderMessages[index];
      await db.add('GaMessages',{ content: message, timestamp: new Date().getTime()},index)
    }
    console.log('Database added successfully')
  } catch (error) {
    console.error('Error adding test messages:', error)
  }
}

/**
 * Clean up the database by deleting it
 */
export const cleanupDB = async (): Promise<void> => {
  try {
    await deleteDB("ChatMessages")
    console.log('Database deleted successfully')
  } catch (error) {
    console.error('Error deleting database:', error)
  }
}
export const GetSpecificMessages = async (DBID: string) => {
  let len:number
  let message:any[]
  try {
    const db = await openDB("ChatMessages", 1,)
    len = await db.count(DBID);
    message = await db.getAll(DBID);

    console.log('Database opened successfully')
  } catch (error) {
    console.error('Error opening database:', error)
  }
  return {len:len,message:message}
}
export const GetSpecificMessage = async (DBID: string, messageID: number) => {
  let message:string
  try {
    const db = await openDB("ChatMessages", 1,)
    message = await db.get(DBID,messageID);

    console.log('Database opened successfully')
  } catch (error) {
    console.error('Error opening database:', error)
  }
  return {message:message}
}
