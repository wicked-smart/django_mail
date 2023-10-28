#include<bits/stdc++.h>
using namespace std;
int diagonalSum(vector<vector<int>>&);
int main()
{
	vector<vector<int>> nums(3, vector<int>(3, 0));

	for(int i=0; i<3; i++)
	{
		for(int j=0; j<3; j++)
		{
			int a;
			cin >> a;
			nums[i][j] = a;
		}
	}

	cout << diagonalSum(nums) << endl;
	return 0;
}

int diagonalSum(vector<vector<int>>& mat) {

        int sum1=0,sum2=0;
        int r = mat.size();
        int c = mat[0].size();

        for(int i=0; i<r; i++)
        {
            for(int j=0; j<c; j++)
            {
                sum1 += mat[i][j];
            }
        }

        for(int i=0; i<r; i++)
        {
            for(int j=c-1; j>=0; j--)
            {
                sum2 += mat[i][j];
            }
        }

        return sum1 + sum2 - mat[r/2][c/2];


    }
	
