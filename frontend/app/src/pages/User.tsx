
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth"
import { auth } from "../../firebase";
import { signOut } from "firebase/auth";
import { useEffect, useState } from "react";
import { config } from "../core/config";

import { Avatar, AvatarImage } from "@/components/ui/avatar"

interface LinkData {
      link_id: number;
      new_link: string;
      click_count: number;
      creator_id: string;
      old_link: string;
      expires_at: string;
      timeRegistered: string;
}

function UserData(){
      const [ user, isLoading ] = useAuth();
      const [ userData, setUserData] = useState(null)

      useEffect(() => {
            
            if (user){ 
                  const handle_fetch = async () => {
                        const token = await user?.getIdToken()
                        const user_id = user?.uid;
                        
                        
                        const request = await fetch(
                              new URL(`user/${user_id}`, config.BASE_API_URL).href,
                              {
                                    method: "GET",
                                    headers: {
                                          "Authorization": `Bearer ${token}`
                                    }
                              }
                        )
                        
                        if (!request.ok){
                              console.error(request.status)
                        }
                        const response = await request.json()
                        console.log("Response is: ", response)
                        setUserData(response)
                  }
                  handle_fetch()
            }
      }, [user]) 


      if (userData){

            const user_profile_pic = userData["presigned_url_profile_pic"]
            const country = userData["country"]
            const displayable_name = userData["displayable_name"]
            const email = userData["email"]

            return (
                  <div> 
                        <h1> YOUR PROFILE </h1>
                        <div className="flex flex-row gap-2"> 
                              <p> Profile pic</p>
                              <Avatar>
                                    <AvatarImage src={user_profile_pic} />
                              </Avatar>
                        </ div>
                        <div className="flex flex-row gap-2"> 
                              <p> Displayable name:</p>
                              <p>{displayable_name}</p>
                        </ div>
                        <div className="flex flex-row gap-2"> 
                              <p> Email: </p>
                              <p>{email}</p>
                        </ div>
                        <div className="flex flex-row gap-2"> 
                              <p> Country: </p>
                              <p>{country}</p>
                        </ div>
                  </ div>
            )
      }
      return  <p> User data NOT ready</p>
}

function UsageData(){

      const [ user, isLoading ] = useAuth();
      const [ usageData, setUsageData] = useState<LinkData[] | null>(null)

      useEffect(() => {
            
            if (user){ 
                  const handle_fetch = async () => {
                        const token = await user?.getIdToken()
                        const user_id = user?.uid;
                        
                        
                        const request = await fetch(
                              new URL(`user/${user_id}/links`, config.BASE_API_URL).href,
                              {
                                    method: "GET",
                                    headers: {
                                          "Authorization": `Bearer ${token}`
                                    }
                              }
                        )
                        
                        if (!request.ok){
                              console.error(request.status)
                        }
                        const response = await request.json()
                        console.log("Response is: ", response)
                        setUsageData(response)
                  }
                  handle_fetch()
            }
      }, [user]) 


      if (usageData){

            return (
                  <div className="w-full max-w-4xl">
                        <h2 className="text-2xl font-bold mb-6 text-gray-800">Your Shortened Links</h2>
                        <div className="bg-white rounded-lg shadow-md overflow-hidden">
                              <div className="overflow-x-auto">
                                    <table className="min-w-full divide-y divide-gray-200">
                                          <thead className="bg-gray-50">
                                                <tr>
                                                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                            Short Link
                                                      </th>
                                                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                            Original URL
                                                      </th>
                                                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                            Clicks
                                                      </th>
                                                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                            Created
                                                      </th>
                                                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                            Expires
                                                      </th>
                                                </tr>
                                          </thead>
                                          <tbody className="bg-white divide-y divide-gray-200">
                                                {usageData.map((link: LinkData, index: number) => {
                                                      const expiresAt = new Date(link.expires_at);
                                                      const now = new Date();
                                                      const isExpired = expiresAt < now;
                                                      const isExpiringSoon = !isExpired && (expiresAt.getTime() - now.getTime()) < 24 * 60 * 60 * 1000; // 24 hours
                                                      
                                                      const getExpirationColor = () => {
                                                            if (isExpired) return 'text-red-600 bg-red-50';
                                                            if (isExpiringSoon) return 'text-orange-600 bg-orange-50';
                                                            return 'text-green-600 bg-green-50';
                                                      };
                                                      
                                                      const getExpirationText = () => {
                                                            if (isExpired) return 'Expired';
                                                            if (isExpiringSoon) return 'Expiring Soon';
                                                            return 'Active';
                                                      };
                                                      
                                                      return (
                                                            <tr key={link.link_id} className="hover:bg-gray-50">
                                                                  <td className="px-6 py-4 whitespace-nowrap">
                                                                        <div className="flex items-center">
                                                                              <span className="text-sm font-medium text-gray-900">
                                                                                    {link.new_link}
                                                                              </span>
                                                                              <button 
                                                                                    className="ml-2 text-blue-600 hover:text-blue-800 text-xs"
                                                                                    onClick={() => navigator.clipboard.writeText(`${window.location.origin}/${link.new_link}`)}
                                                                              >
                                                                                    Copy
                                                                              </button>
                                                                        </div>
                                                                  </td>
                                                                  <td className="px-6 py-4">
                                                                        <div className="max-w-xs truncate">
                                                                              <a 
                                                                                    href={link.old_link} 
                                                                                    target="_blank" 
                                                                                    rel="noopener noreferrer"
                                                                                    className="text-sm text-blue-600 hover:text-blue-800 truncate block"
                                                                                    title={link.old_link}
                                                                              >
                                                                                    {link.old_link}
                                                                              </a>
                                                                        </div>
                                                                  </td>
                                                                  <td className="px-6 py-4 whitespace-nowrap">
                                                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                                              {link.click_count}
                                                                        </span>
                                                                  </td>
                                                                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                                        {new Date(link.timeRegistered).toLocaleDateString()}
                                                                  </td>
                                                                  <td className="px-6 py-4 whitespace-nowrap">
                                                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getExpirationColor()}`}>
                                                                              {getExpirationText()}
                                                                        </span>
                                                                        <div className="text-xs text-gray-500 mt-1">
                                                                              {expiresAt.toLocaleDateString()}
                                                                        </div>
                                                                  </td>
                                                            </tr>
                                                      );
                                                })}
                                          </tbody>
                                    </table>
                              </div>
                        </div>
                        {usageData.length === 0 && (
                              <div className="text-center py-8 text-gray-500">
                                    No shortened links found. Create your first link!
                              </div>
                        )}
                  </div>
            )
      }
      



      return (
            <p> Usage data NOT ready</p>
      )
}


export default function User(){
      const [ user, isLoading ] = useAuth();
      const [ userData, setUserData] = useState(null)
      
      
      const handleSignOut = async () => {
            await signOut(auth)
      }

      if (isLoading){
            return <p> Im loading...</p>
      }
      
      return (
            <div className="flex flex-col w-full h-full"> 
                  <div className="flex flex-row gap-3">
                        <UserData />
                        <UsageData />
                  </div>
                  <div className="flex w-full h-full"> 
                        <button className="btn-primary m-auto" onClick={handleSignOut}> Sign out</button>
                  </div>
            </div>
      )
}