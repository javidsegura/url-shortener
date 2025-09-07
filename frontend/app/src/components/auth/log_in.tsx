import { useState } from "react";
import { auth } from "../../../firebase"
import { signInWithEmailAndPassword} from 'firebase/auth';
import { useForm } from "../../hooks/useForm";


export default function LogInForm(){

      const [formData, handleFormChange] = useForm({
            "email" : "",
            "password": ""
      })

      const handleSignUpWithEmail = async (event) => {
            event.preventDefault();
            try {
                  const userCredential = await signInWithEmailAndPassword(auth, formData.email, formData.password)
                  const user = userCredential.user 
                  console.error("User signed up:", user)
            }
            catch (error){
                  console.log("Error occured", error.message)
            }
      }


      return ( 
            <form onSubmit={handleSignUpWithEmail} className="flex flex-col">
                        <label>
                              Email: 
                              <input type="email" name="email" onChange={handleFormChange} value={formData.email}></input>
                        </label>
                        <label>
                              Password: 
                              <input type="password" name="password" onChange={handleFormChange} value={formData.password}></input>
                        </label>
                        <input type="submit" className="btn-primary" />
            </form>
      )
}