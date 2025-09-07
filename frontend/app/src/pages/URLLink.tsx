import { useState } from "react"
import { config } from "../core/config"
import { useAuth } from "../hooks/useAuth"


export default function URLLink(){

      const [ user, isLoading ] = useAuth();
      const [data, setData] = useState(null)
      const [error, setError] = useState(null)
      const [loading, setLoading] = useState<boolean>(false)

      const handle_button_click = async () => {
                  setError(null)
                  setData(null)
                  setLoading(true)
                  const token = await user?.getIdToken()
                  try { 
                        const response = await fetch(
                              new URL("health", config.BASE_API_URL).href,
                              {
                                    method: "GET",
                                    headers: {
                                          "Authorization": `Bearer ${token}`
                                    }
                              }
                        )

                        if (!response.ok){
                              throw new Error(`HTTP error with code status ${response.status}`)
                        }

                        const data = await response.json()
                        setData(data)
                  }
                  catch (error) {
                        setError(error.message)
                  }
                  finally {
                        setLoading(false)
                  }
            }
      
      const handle_form_submission = async (event) => {
            event.preventDefault()

            setError(null)
            setData(null)
            setLoading(true)
            const token = await user?.getIdToken()


            const formdata = new FormData(event.target)

            const original_url = formdata.get("original_url")
            const expires_in = formdata.get("expires_in")

            console.log('Sending to backend:', { original_url, expires_in })


            
            try {
                  const response = await fetch(
                        new URL("link",config.BASE_API_URL).href,
                        {
                              method: "POST",
                              headers: {
                                    "Content-type": "application/json",
                                    "Authorization": `Bearer ${token}`
                              },
                              body: JSON.stringify(
                                    {
                                          original_url: original_url,
                                          expires_in: expires_in
                                    }
                              )
                        }
                  )

                  if (!response.ok){
                        throw new Error(`HTTP error with code status ${response.status}`)
                  }

                  const result = await response.json()
                  setData(result)
            }
            catch (error){
                  setError(error.message)
            }
            finally {
                  setLoading(false)
            }
      }
      

      return (
            <div id="main-space" className="flex flex-row w-full h-full">
                  <div className="centered-box border-primary-600">
                        <div id="testing_invokation_area" className="h-[90%]"> 
                              <p> TESTING ENDPOINTS</p>
                              <div id="endpoint1" className="flex flex-row gap-2">
                                    <h1> - Health Endpoint </h1>
                                    <button 
                                          className="btn-secondary"
                                          onClick={() => handle_button_click()}
                                          disabled={loading}> Invoke </button>
                              </div>
                              <div id="endpoint2" className="flex flex-row gap-2">
                                    <h1> - URL Endpoint </h1>
                                    <form onSubmit={handle_form_submission} className="border-2 flex flex-col w-full">
                                          <label className="p-2"> 
                                                URL link: 
                                                <input type="text" name="original_url" placeholder="Long link here..." className="ml-2"/>
                                          </label>
                                          <label className="p-2">
                                                Expires in (minutes):
                                                <input type="number" name="expires_in" className="ml-2" />
                                          </label>
                                          <input type="submit" className="btn-secondary" />
                                    </form>
                              </div>
                        </div>
                        <div id="endpoints_response">
                              <p> Endpoint response: </p>
                              {loading && <p className="text-3xl"> Loading response...</p>}
                              {data && (
                                    <pre> 
                                          {JSON.stringify(data, null, 2)}
                                    </pre>
                              )}
                              {error && <p> {error}</p>}
                        </div>
                  </div>
           </div>
      )
}