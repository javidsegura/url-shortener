import { FileField } from "../components/forms/fileField"
import { useForm } from "../hooks/useForm"
import { config } from "../core/config";
import { useAuth } from "../hooks/useAuth";
import { useState } from "react";

export default function TestPage(){

      const [ user, loading ] = useAuth()
      const [data, setData ] = useState();
 
      const handle_fetch = async () => {
            const token = await user?.getIdToken()
            const user_id = user["uid"];
            
            const request = await fetch(
                  new URL(`test`, config.BASE_API_URL).href,
                  {
                        method: "GET",
                        headers: {
                              "Authorization": `Bearer ${token}`
                        }
                  }
            )

            if (!request.ok){
                  console.error(request.error)
            }
            const response = await request.json()
            setData(response)
      }

      return (<>
            <button className="btn-primary" onClick={handle_fetch}> Fetch test</button>
            <pre> {JSON.stringify(data, null, 2)}</pre>
            <img src={data?.["presigned-url-profile-pic"]} />
      </>)

}