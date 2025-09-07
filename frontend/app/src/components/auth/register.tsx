import { auth } from "../../../firebase"
import { createUserWithEmailAndPassword, sendEmailVerification, updateProfile} from 'firebase/auth';
import { SelectField } from "../forms/optionsField";
import { TextField } from "../forms/textField";
import { FileField } from "../forms/fileField";

import { COUNTRIES_LIST } from "../../data/countries";
import { useForm } from "../../hooks/useForm";
import { config } from "../../core/config";

export default function RegisterForm(){

      const [formContent, handleFormChange] = useForm({
            "name": "",
            "email": "",
            "password": "",
            "country": "",
            "profile_pic": ""
      });


      const buttons = [
            {
                Component: TextField,
                props: {
                    fieldName: "name",
                    fieldDescription: "Insert here your name",
                    fieldType: "text",
                    fieldOnChange: handleFormChange,
                    fieldValue: formContent.name,
                },
            },
            {
                Component: TextField,
                props: {
                    fieldName: "email",
                    fieldDescription: "Insert here your email",
                    fieldType: "email",
                    fieldOnChange: handleFormChange,
                    fieldValue: formContent.email,
                },
            },
            {
                Component: TextField,
                props: {
                    fieldName: "password",
                    fieldDescription: "Insert here your password",
                    fieldType: "password", // Corrected fieldType
                    fieldOnChange: handleFormChange,
                    fieldValue: formContent.password, // Corrected fieldValue
                },
            },
            {
                Component: SelectField,
                props: {
                    fieldName: "country",
                    fieldDescription: "A great description",
                    fieldOptions: COUNTRIES_LIST,
                    fieldOnChange: handleFormChange,
                    fieldValue: formContent.country,
                },
            },
            {
                Component: FileField,
                props: {
                    fieldName: "profile_pic",
                    fieldDescription: "Upload an image",
                    multiple: false,
                    accept: "image*",
                    fieldOnChange: handleFormChange,
                },
            },
        ];

      const handleRegisterWithEmail = async (event) => {
            event.preventDefault();

            // 1) Attempt to upload profile pic
            try {
                  console.log("About to send: ", formContent)
                  console.log("About to send for profile pic: ", JSON.stringify(
                        {"file_name": formContent.profile_pic.name,
                        "content_type": formContent.profile_pic.type
                        }))


                  const preSignedUrlResponse = await fetch(
                        new URL("user/profile_pic", config.BASE_API_URL).href,
                        {
                              method: "POST",
                              body: JSON.stringify(
                                                {"file_name": formContent.profile_pic.name,
                                                "content_type": formContent.profile_pic.type
                                                }),
                              headers: {
                                    "Content-Type": "application/json"
                              }

                        }
                  )
                  if (!preSignedUrlResponse.ok){
                        throw new Error(preSignedUrlResponse.error)
                  }
                  const data = await preSignedUrlResponse.json();
                  const presigned_url = data.presigned_url
                  const s3_file_name = data.s3_file_name

                  const fileUploadResponse = await fetch(
                        presigned_url,
                        {
                              method: "PUT",
                              body: formContent.profile_pic,
                              headers: {
                                    "Content-Type": formContent.profile_pic.type
                              }
                        }
                  )
                  if (!fileUploadResponse.ok){
                        throw new Error(preSignedUrlResponse.error)
                  }
           

            // 3. Register user 
                  console.log("User signing up with following data:", formContent )
                  const userCredentials = await createUserWithEmailAndPassword(auth, 
                        formContent.email, 
                        formContent.password)
                  await sendEmailVerification(userCredentials.user)
                  await updateProfile(userCredentials.user, {
                        displayName: formContent.name,
                  })
                  
            

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
                              "displayable_name": formContent.name,
                              "email": formContent.email,
                              "country": formContent.country,
                              "profile_pic_object_name": s3_file_name
                        })
                  }
                  )
                  if (!db_response.ok){
                        throw new Error(preSignedUrlResponse.error)
                  }

            }
            catch (error) {
                  console.log("Error occured", error.message)
            }

                  

      }

      return ( 
            <form onSubmit={handleRegisterWithEmail}>
                  {
                        buttons.map((item, index) => (
                              <item.Component key={index} {...item.props} />
                        ))
                  }
                  <input type="submit" />
            </form>
      )


}