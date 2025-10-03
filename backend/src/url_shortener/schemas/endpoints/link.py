from datetime import datetime

from pydantic import BaseModel


class DataURL(BaseModel):
	short_url: str
	original_url: str
	created_at: datetime
	expires_at: datetime


class URLShorteningResponse(BaseModel):
	success: bool
	data: DataURL


class URLShorteningRequest(BaseModel):
	original_url: str
	expires_in: int


class ListOfLinksResponse(BaseModel):
	link_id: int
	creator_id: str
	old_link: str
	new_link: str
	expires_at: datetime
	timeRegistered: datetime
	click_count: int