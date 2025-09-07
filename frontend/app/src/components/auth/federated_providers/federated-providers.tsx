import { GoogleAuthProvider, signInWithPopup } from 'firebase/auth';
import { auth } from "../../../../firebase";
import { config } from '@/core/config';

export function GoogleAuthButton(){
      const handleRegisterWithGoogle = async (event) => {
            event.preventDefault();

            try {

            // 3. Register user 
                  const provider = new GoogleAuthProvider()
                  const userCredentials = await signInWithPopup(auth, provider)
                  const user = userCredentials.user 
                  console.error("User signed up:", user)
                  // await sendEmailVerification(userCredentials.user)
            

            // 2. Store  user info in db
                  const db_response = await fetch(
                  new URL("user", config.BASE_API_URL).href,
                  {
                        method: "POST",
                        headers: {
                              "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                              "user_id": userCredentials.user.uid,
                              "displayable_name": userCredentials.user.displayName,
                              "email": userCredentials.user.email,
                              "country": "ES",
                              "profile_pic_object_name": userCredentials.user.photoURL
                        })
                  }
                  )
                  if (!db_response.ok){
                        throw new Error("An error occured")
                  }

            }
            catch (error) {
                  console.log("Error occured", error.message)
            }
      }
      
      return ( 
            <button onClick={handleRegisterWithGoogle} className='cursor-pointer'> THIS IS SOME GOOGLE BUTTON </button>
      )
}
 