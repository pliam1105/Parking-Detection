#include "rapidjson/filereadstream.h"
#include "rapidjson/filewritestream.h"
#include "rapidjson/document.h"
#include <rapidjson/writer.h>
#include <bits/stdc++.h> 

using namespace rapidjson;
using namespace std;

typedef pair<int,int> pt;
//input data
vector<vector<vector<bool>>> mask_ar;
vector<int> class_ids;
vector<vector<pt>> parking_spaces;//each parking space has {p1,p2,p3,p4} where p_i={x,y} (as pair)
vector<vector<double>> overlaps;

bool ccw(pt p1,pt p2,pt p3){
	int x1=p1.first,x2=p2.first,x3=p3.first;
	int y1=p1.second,y2=p2.second,y3=p3.second;
	return (x1*y2+x2*y3+x3*y1)>=(x2*y1+x3*y2+x1*y3);
}

bool pt_in_poly(pt p,vector<pt> poly){
	bool b1=ccw(p,poly[0],poly[1]),b2=ccw(p,poly[1],poly[2]),b3=ccw(p,poly[2],poly[3]),b4=ccw(p,poly[3],poly[0]);
	return (b1==b2)&&(b1==b3)&&(b1==b4);
}

void compute_overlaps(){
	int rx=mask_ar.size();
	int ry=mask_ar[0].size();
	int rob=mask_ar[0][0].size();
	vector<vector<pt>> cars;
	vector<vector<pt>> parks;
	for(int i=0;i<rob;i++){
		cars.push_back(vector<pt>());
	}
	vector<int> obj;
	for(int i=0;i<rob;i++){
		if(class_ids[i]==3||class_ids[i]==8||class_ids[i]==6){
			obj.push_back(i);
		}
	}
	for(int x=0;x<rx;x++){
		for(int y=0;y<ry;y++){
			for(int ob:obj){
				if(mask_ar[x][y][ob]) cars[ob].push_back({x,y});
			}
		}
	}
	//now we have cars masks
	//now lets find parking masks
	for(int i=0;i<parking_spaces.size();i++){
		parks.push_back(vector<pt>());
		for(int x=0;x<rx;x++){
			for(int y=0;y<ry;y++){
				if(pt_in_poly({y,x},parking_spaces[i])) parks[i].push_back({x,y});
			}
		}
	}
	for(int i=0;i<parks.size();i++){
		sort(parks[i].begin(),parks[i].end());
	}
	for(int i=0;i<cars.size();i++){
		sort(cars[i].begin(),cars[i].end());
	}
	for(int i=0;i<parks.size();i++){
		overlaps.push_back(vector<double>());
		for(int j=0;j<cars.size();j++){
			overlaps[i].push_back(0);
			//now compute overlaps[i][j]
			vector<pt> vinter,vuni;
			set_intersection(parks[i].begin(),parks[i].end(),cars[i].begin(),cars[i].end(),back_inserter(vinter));
			set_union(parks[i].begin(),parks[i].end(),cars[i].begin(),cars[i].end(),back_inserter(vuni));
			overlaps[i][j]=((double)vinter.size())/((double)vuni.size());
		}
	}
}

int main(){
	FILE* fp = fopen("pytoc.json", "r");
 
	char readBuffer[65536];
	FileReadStream is(fp, readBuffer, sizeof(readBuffer));
	 
	Document din;
	din.ParseStream(is);
	 
	fclose(fp);

	//computation
	const Value& maskdata=din["masks"];
	assert(maskdata.IsArray());
	for(SizeType i=0; i<maskdata.Size();i++){
		mask_ar.push_back(vector<vector<bool>>());
		const Value& maskdatai=maskdata[i];
		assert(maskdatai.IsArray());
		for(SizeType j=0;j<maskdatai.Size();j++){
			mask_ar[i].push_back(vector<bool>());
			const Value& maskdataij=maskdata[i][j];
			assert(maskdataij.IsArray());
			for(SizeType k=0;k<maskdataij.Size();k++){
				assert(maskdataij[k].IsBool());
				mask_ar[i][j].push_back(maskdataij[k].GetBool());
			}
		}
	}
	const Value& classdata=din["class_ids"];
	assert(classdata.IsArray());
	for(SizeType i=0;i<classdata.Size();i++){
		assert(classdata[i].IsInt());
		class_ids.push_back(classdata[i].GetInt());
	}
	const Value& parkdata=din["parking"];
	assert(parkdata.IsArray());
	for(SizeType i=0;i<parkdata.Size();i++){
		parking_spaces.push_back(vector<pt>());
		const Value& parkdatai=parkdata[i];
		assert(parkdatai.IsArray());
		for(SizeType j=0;j<parkdatai.Size();j++){
			const Value& parkdataij=parkdatai[j];
			assert(parkdataij.IsArray());
			assert(parkdataij[0].IsDouble());
			assert(parkdataij[1].IsDouble());
			parking_spaces[i].push_back({(int)parkdataij[0].GetDouble(),(int)parkdataij[1].GetDouble()});
		}
	}
	
	compute_overlaps();
	
	Document dout(kArrayType);
	Document::AllocatorType& allocator = dout.GetAllocator();
	for(auto v: overlaps){
		Value overi(kArrayType);
		for(auto x:v){
			overi.PushBack(Value().SetDouble(x),allocator);
		}
		dout.PushBack(overi,allocator);
	}
	
	
	fp = fopen("ctopy.json", "w");
	 
	char writeBuffer[65536];
	FileWriteStream os(fp, writeBuffer, sizeof(writeBuffer));
	 
	Writer<FileWriteStream> writer(os);
	dout.Accept(writer);
	 
	fclose(fp);
}

