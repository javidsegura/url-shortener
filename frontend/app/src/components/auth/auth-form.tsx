
import { useState } from "react"
import LogInForm from "./log_in"
import RegisterForm from "./register"
import { GoogleAuthButton } from "./federated_providers/federated-providers"

export default function AuthForm(){

      const [registerActive, setRegisterActive ] = useState(true) 

      return ( 
            <div id="main-space" className="flex flex-row w-full h-full"> 
                  <div className="centered-box border-primary-500 flex flex-col">
                        <h1 className="text-2xl mx-auto">
                                                      {registerActive ? "Register here" : 
                                                       "Log-in here" } </h1>
                        <div id="manual-form-with-federated-providers" className="flex flex-row h-full w-full"> 
                              <div id="form-layout" className="w-2/3 m-auto"> 
                                    {registerActive ? 
                                          <RegisterForm setRegisterActive={setRegisterActive} />
                                          :
                                          <LogInForm setRegisterActive={setRegisterActive}/>
                                    }
                              </div>
                              <GoogleAuthButton />
                        </div>
                        <p className="m-auto cursor-pointer" onClick={() => setRegisterActive(!registerActive)}> Or <u>
                               {registerActive ?
                               "log-in":
                               "register"} here
                               </u>
                        </p>
                  </div>
            </div>
      )
}