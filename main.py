import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from StringIO import StringIO
import csv, json, time, httplib, sys
from optparse import OptionParser


def main():
    usage = 'Use: %prog [options] arg1'
    parser = OptionParser(usage=usage)
    parser.add_option('-s', '--setup', dest='setup_flag', action='store_true', default=False,help='Run the Setup')
    parser.add_option('-q','--query', dest='query_flag', action='store_true', default=False, help='Run a filter query through the info')
    (options, args) = parser.parse_args()

    if options.query_flag:
        df = pd.read_csv('final.csv')
        filtering(df)
        sys.exit()
    set_really = 1
    if options.setup_flag:
        print '[+] Are you sure you want to continue setup might take several hours?'
        set_really = raw_input('[y] / [n] : ')

    if 'n' in set_really:
        print '[+] Setup start not picked exiting'
        sys.exit()
    print "Inside main"
    filee = file('list_of_ips.txt').read().replace('\n', ' ')
    fileee = filee.split(' ')
    print len(fileee)
    ip_list = list()
    counter = 0
    triggered = 0
    new_ip = ''
    first_quad = 1
    for i in fileee:
        f_split = i.split('.')
        if len(f_split) >= 3:
            for j in f_split:
                if len(j) > 3:
                    j = j[0:3]
                if len(j) <=3:
                    try:
                        new_j = int(j)
                        triggered = 1
                        counter += 1
                    except:
                        triggered = 0
                        counter = 0
                        new_ip = ''
                        first_quad = 1
                        pass
                    if triggered and new_j <= 255:
                        if first_quad:
                            new_ip = str(new_j)
                            first_quad = 0
                        else:
                            new_ip = new_ip+'.'+str(new_j)
                        if counter == 4:
                            ip_list.append(new_ip)
                            counter = 0
                            new_ip = ''
                            triggered = 0
                            first_quad = 1
                    else:
                        counter = 0
                        new_ip = ''
                        triggered = 0
                        first_quad = 1



    print len(ip_list)
    my_df = pd.DataFrame(ip_list, columns=['ip'])
   # my_df.to_csv('ip.csv', index=False)
    geo(my_df)

def geo(df):
    org_list = list()
    loc_list = list()
    postal_list = list()
    city_list = list()
    country_list = list()
    region_list = list()
    new_df = pd.DataFrame(columns=['country_code', 'region_code', 'city','zip_code', 'latitude', 'longitude'])
    cc = 0
    hdr = {'User-Agent' : 'super geoloc1111 bot'}
    conn = httplib.HTTPConnection('freegeoip.net')
    for i in df['ip']:
        conn.request('GET', '/json/'+str(i), headers=hdr)
        response = conn.getresponse()
        data = json.load(response)
        d = {}
        for i in new_df.columns:
            if i not in data:
                d[i] = 'NA'
            else:
                if data[i] == '':
                    d[i] = 'NA'
                else:
                    d[i] = data[i]
        new_df = new_df.append({
            'country_code': d['country_code'],
            'region_code': d['region_code'],
            'city': d['city'].encode('utf-8'),
            'zip_code': d['zip_code'],
            'latitude': d['latitude'],
            'longitude': d['longitude']
            }, ignore_index=True)
        cc += 1
        if cc % 100 == 0:
            print 'Ran through '+str(cc)+' ips'

    df.reset_index(drop=True, inplace=True)
    new_df.reset_index(drop=True, inplace=True)
    all_df = pd.concat([df, new_df], axis=1)
    all_df.to_csv('ips_geo.csv', index=False)

def rdap(df):
    new_df = pd.DataFrame(columns=['handle', 'name', 'last_changed', 'registration'])
    hdr = {'User-Agent' : 'super rDabber11'}
    conn = httplib.HTTPConnection('rdap.arin.net')
    cc = 0
    for i in df['ip']:
        try:
            conn.request('GET', '/registry/ip/'+str(i)+'/', headers=hdr)
            response = conn.getresponse()
            data = json.load(response)
        except:
            print "[+] Reopening conn"
            hdr = {'User-Agent' : 'supreme dapper'}
            conn = httplib.HTTPConnection('rdap.arin.net')
            conn.request('GET', '/registry/ip/'+str(i)+'/', headers=hdr)
            response = conn.getresponse()
            data = json.load(response)
        d = {}
        in_cc =0
        for j in new_df.columns:
            if in_cc == 2:
                break
            if j not in data:
                d[j] = 'NA'
            else:
                if data[j] == '':
                    d[j] = 'NA'
                else:
                    d[j] = data[j]
            in_cc += 1
        d['last_changed'] = 'NA'
        d['registration'] = 'NA'
        try:
            for j in data['events']:
                if j['eventAction'] == 'last changed':
                    d['last_changed'] = j['eventDate'].split('T')[0]
                if j['eventAction'] == 'registration':
                    d['registration'] = j['eventDate'].split('T')[0]
        except:
            pass
        new_df = new_df.append({
            'handle': d['handle'],
            'name': d['name'],
            'last_changed': d['last_changed'],
            'registration': d['registration']
            }, ignore_index=True)
        cc +=1
        if cc % 100 == 0:
            print '[+] Scanned through '+str(cc)+' ips'
        if cc %2 ==0:
            time.sleep(1)
    print new_df.head()
    df.reset_index(drop=True, inplace=True)
    new_df.reset_index(drop=True, inplace=True)
    all_df = pd.concat([df, new_df], axis=1)
    all_df.to_csv('final.csv', index=False)

def filtering(df):
    keys = ['ip', 'country_code', 'region_code', 'city', 'zip_code', 'latitude', 'longitude', 'handle', 'name', 'last_changed', 'registration']
    print '[+] Please enter search query\
            For more in depth info look to the documentiation'
    print '[+] For example to select a single column.'
    print '[+] Type *S (ip, city, etc.) *W (col = value)'
    print '[+] You can select all cols with just * as in: \
            *S * *W (city*IDenver, Chicago, Dallas) *O (region_code=IL) *A (city!=Chicago)\
            The above  statememnt will select all columns where the city is \
            in the list provided of Denver, Chicago, and Dallas along with the \
            other part of the of statement which looks for info in Illinois and\
            not in Chicago. At the end the two get combined into one data frame.'
    print '[+] The keys for the data are:'
    print '[+] ip, country_code, region_code, city, zip_code, latitude, longitude, handle, name, last_changed, registration'
    query = raw_input('--->')
    print '[+] The query is: '+str(query)
    if query.find('*S', 0, 3) != -1:
        new_df = select_q(df, query)
        print new_df.head(50)
        print '[+] Graph it?'
        gg = 0
        gg = raw_input('[y] / [n]')
        if 'y' in gg:
            graph_it(new_df)
        print '[+] Would you like to make another query?'
        another_one = raw_input('[y] / [n]')
        if 'y' in another_one:
            filtering(df)
        else:
            print '[+] Thanks for using the program'
            sys.exit()
    else:
        print '[+] Invalid query please try again'
        filtering(df)

def graph_it(df):
    for i in df.columns:
        g = sns.countplot(x=i, data=df)
        for lib in g.get_xticklabels():
            lib.set_rotation(45)
        #g.set_xticklabels(rotation=90)
        plt.title(i, y=1.0)
        sns.plt.show()


def select_q(df, query):
    if query.find('*W') == -1:
        cols = query.replace('*S', '').replace(' ','').split(',')
        if '*' in cols:
            cols = ['ip', 'country_code', 'region_code', 'city', 'zip_code', 'latitude', 'longitude', 'handle', 'name', 'last_changed', 'registration']
        new_df = df[cols]
        #print new_df.head()
        return new_df
    else:
        wloc = query.find('*W') + 3
        new_q = query[wloc:]
        select_qq = query[:(wloc - 3)]
        #print '[+] Where query is :'+str(new_q)
        new_df = where_q(df, new_q)
        #print new_df.head()
        #print select_qq
        return select_q(new_df, select_qq)

def or_q(df, query):
    new_qs = query.split('*O')
    all_df = pd.DataFrame(columns=['ip','country_code', 'region_code', 'city', 'zip_code','latitude','longitude','handle','name', 'last_changed','registration'])
    for i in new_qs:
        i = i.replace(' ','')
        print 'About to make this query from or'
        print i
        new_df = where_q(df, i)
        all_df = pd.concat([all_df, new_df])
    return all_df


def where_q(df, query):
    if len(query.split('*O')) > 1:
        return or_q(df, query)
    else:
        comp = query.find(')')
        query_w = query[:comp]
        query_a = query[comp:]
        do_another = query_a.find('*A')
        query_w = query_w[1:].strip(' ')
        equal = 0
        not_equal = 0
        in_contain = 0
        if query_w.find('!=') != -1:
            not_equal = 1
        elif query_w.find('=') != -1:
            equal = 1
        elif query_w.find('*I') != -1:
            in_contain = 1
            query_w = query_w.split('*I')
        if not_equal:
            query_w = query_w.split('!=')
        elif equal:
            query_w = query_w.split('=')

        cols = df.columns
        #print 'This is the query col'+str(query_w[0])
        if query_w[0] not in cols:
            print '[+] Invalid column selected going back to initial'
        else:
            if not_equal:
                new_df = df.loc[df[query_w[0]] != query_w[1]]
                if do_another != -1:
                    query_a = query_a[2:]
                    return where_q(new_df, query_a)
                else:
                    return new_df
            elif equal:
                new_df = df.loc[df[query_w[0]] == query_w[1]]
                if do_another != -1:
                    query_a = query_a.replace(' ','')[3:]
                    print 'This is query a'
                    print query_a
                    return where_q(new_df, query_a)
                else:
                    return new_df
            elif in_contain:
                da_list = query_w[1].replace(' ', '').split(',')
                new_df = df.loc[df[query_w[0]] == da_list[0]]
                ii = 0
                for i in da_list:
                    if ii:
                        new_df1 = df.loc[df[query_w[0]] == i]
                        new_df = pd.concat([new_df, new_df1])
                    else:
                        ii = 1
                if do_another != -1:
                    query_a = query_a[2:]
                    return where_q(new_df, query_a)
                else:
                    return new_df
            #new_df = df.loc[df[qq[0]] == qq[1]]
            #print new_df.head()



if __name__ == "__main__":
    main()
